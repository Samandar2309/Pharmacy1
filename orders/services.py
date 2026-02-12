from decimal import Decimal
from typing import List

from django.db import transaction
from django.db.models import F
from django.core.exceptions import ValidationError
from django.utils import timezone

from orders.models import Cart, Order, OrderItem, CartItem
from products.models import Product
from notifications.services import NotificationService


# =========================================================
# EXCEPTIONS
# =========================================================

class CartEmptyError(Exception):
    pass


class InsufficientStockError(Exception):
    pass


class InvalidOrderStatusError(Exception):
    pass


# =========================================================
# CART SERVICE
# =========================================================

class CartService:
    """
    Cart management service
    """

    @staticmethod
    @transaction.atomic
    def add_to_cart(*, user, product_id: int, quantity: int = 1):
        """
        Savatga mahsulot qo'shish yoki miqdorni oshirish
        """
        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            raise ValidationError("Mahsulot topilmadi")

        if product.stock < quantity:
            raise ValidationError("Omborda yetarli mahsulot yo'q")

        cart, _ = Cart.objects.get_or_create(user=user)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save(update_fields=['quantity'])

        return cart_item

    @staticmethod
    @transaction.atomic
    def remove_from_cart(*, user, item_id: int):
        """
        Savatdan o'chirish
        """
        try:
            cart = Cart.objects.get(user=user)
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
            cart_item.delete()
        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            raise ValidationError("CartItem topilmadi")

    @staticmethod
    @transaction.atomic
    def update_quantity(*, user, item_id: int, quantity: int):
        """
        Miqdorni o'zgartirish
        """
        if quantity <= 0:
            raise ValidationError("Miqdor 0 dan katta bo'lishi kerak")

        try:
            cart = Cart.objects.get(user=user)
            cart_item = CartItem.objects.get(id=item_id, cart=cart)

            if cart_item.product.stock < quantity:
                raise ValidationError("Omborda yetarli mahsulot yo'q")

            cart_item.quantity = quantity
            cart_item.save(update_fields=['quantity'])

            return cart_item

        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            raise ValidationError("CartItem topilmadi")

    @staticmethod
    @transaction.atomic
    def clear_cart(*, user):
        """
        Savatchani tozalash
        """
        try:
            cart = Cart.objects.get(user=user)
            cart.items.all().delete()
        except Cart.DoesNotExist:
            pass


# =========================================================
# 🔥 STOCK SERVICE (race-safe)
# =========================================================

class StockService:
    """
    🔥 Yagona stock manager
    """

    @staticmethod
    def decrease(product_id: int, quantity: int):
        updated = Product.objects.filter(
            id=product_id,
            stock__gte=quantity
        ).update(stock=F("stock") - quantity)

        if updated == 0:
            raise InsufficientStockError("Omborda yetarli mahsulot yo‘q")

    @staticmethod
    def increase(product_id: int, quantity: int):
        Product.objects.filter(id=product_id).update(
            stock=F("stock") + quantity
        )


# =========================================================
# 🔥 ORDER CREATION (FINAL PRODUCTION VERSION)
# =========================================================

class OrderCreationService:

    @staticmethod
    @transaction.atomic
    def checkout(*, user, delivery_address: str) -> Order:

        # -----------------------------------------
        # CART LOCK
        # -----------------------------------------
        cart = (
            Cart.objects
            .select_for_update()
            .prefetch_related("items__product")
            .filter(user=user)
            .first()
        )

        if not cart or not cart.items.exists():
            raise CartEmptyError("Savatcha bo‘sh")

        today = timezone.now().date()

        needs_prescription = False
        total_price = Decimal("0.00")
        order_items: List[OrderItem] = []

        # -----------------------------------------
        # VALIDATION + PRICE FREEZE
        # -----------------------------------------
        for item in cart.items.all():

            product = item.product

            # 🔥 expiry protection
            if product.expiry_date and product.expiry_date < today:
                raise ValidationError(f"{product.name} muddati o‘tgan")

            if product.requires_prescription:
                needs_prescription = True

            subtotal = product.price * item.quantity
            total_price += subtotal

            order_items.append(
                OrderItem(
                    product=product,
                    quantity=item.quantity,
                    price=product.price
                )
            )

        # -----------------------------------------
        # CREATE ORDER
        # -----------------------------------------
        status = (
            Order.Status.AWAITING_PRESCRIPTION
            if needs_prescription
            else Order.Status.AWAITING_PAYMENT
        )

        order = Order.objects.create(
            user=user,
            delivery_address=delivery_address,
            total_price=total_price,
            needs_prescription=needs_prescription,
            status=status
        )

        for obj in order_items:
            obj.order = order

        OrderItem.objects.bulk_create(order_items)

        # -----------------------------------------
        # STOCK ATOMIC DECREASE (SAFE)
        # -----------------------------------------
        for obj in order_items:
            StockService.decrease(obj.product_id, obj.quantity)

        cart.items.all().delete()

        # -----------------------------------------
        # 🔥 NOTIFICATION
        # -----------------------------------------
        NotificationService.order_created(order)

        return order


# =========================================================
# 🔥 STATUS SERVICE (single source of truth)
# =========================================================

class OrderStatusService:

    ROLE_PERMISSIONS = {
        Order.Status.PREPARING: {"operator", "admin"},
        Order.Status.READY_FOR_DELIVERY: {"operator", "admin"},
        Order.Status.ON_THE_WAY: {"courier", "admin"},
        Order.Status.DELIVERED: {"courier", "admin"},
    }

    @staticmethod
    @transaction.atomic
    def change_status(*, order: Order, new_status: str, actor):

        role = getattr(actor, "role", None)

        allowed_roles = OrderStatusService.ROLE_PERMISSIONS.get(new_status)

        if allowed_roles and role not in allowed_roles:
            raise ValidationError("Ruxsat yo‘q")

        # 🔥 ONLY via model method
        order.change_status(new_status, changed_by=actor)

        NotificationService.order_status_changed(order)

        return order


# =========================================================
# 🔥 CANCEL SERVICE
# =========================================================

class OrderCancelService:

    @staticmethod
    @transaction.atomic
    def cancel(*, order: Order, actor):

        if order.status not in {
            Order.Status.DRAFT,
            Order.Status.AWAITING_PAYMENT,
            Order.Status.AWAITING_PRESCRIPTION
        }:
            raise InvalidOrderStatusError("Bekor qilib bo‘lmaydi")

        for item in order.items.select_for_update():
            StockService.increase(item.product_id, item.quantity)

        order.change_status(Order.Status.CANCELLED, changed_by=actor)

        NotificationService.order_cancelled(order)

        return order