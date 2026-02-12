from rest_framework import status, permissions, viewsets, mixins
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import ValidationError

from orders.models import Order
from orders.serializers import (
    CartSerializer,
    OrderSerializer,
    OrderCreateSerializer,
    OrderStatusChangeSerializer,
    OrderCancelSerializer,
)

from orders.selectors import CartSelector, OrderSelector
from orders.permissions import OrderPermission

from orders.services import (
    CartEmptyError,
    InsufficientStockError,
    InvalidOrderStatusError,
    CartService,
)


# =========================================================
# PAGINATION
# =========================================================

class OrderPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


# =========================================================
# CART
# =========================================================

class CartViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        cart = CartSelector.get_user_cart(request.user)
        return Response(CartSerializer(cart).data)

    @action(detail=False, methods=['post'])
    def add(self, request):
        """
        Savatga mahsulot qo'shish
        POST /api/v3/orders/cart/add/
        {
            "product_id": 1,
            "quantity": 2
        }
        """
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)

        if not product_id:
            raise ValidationError({"product_id": "Bu maydon majburiy"})

        try:
            cart_item = CartService.add_to_cart(
                user=request.user,
                product_id=product_id,
                quantity=quantity
            )
            
            cart = CartSelector.get_user_cart(request.user)
            return Response(CartSerializer(cart).data, status=status.HTTP_201_CREATED)

        except Exception as e:
            raise ValidationError({"detail": str(e)})

    @action(detail=True, methods=['delete'])
    def remove(self, request, pk=None):
        """
        Savatdan o'chirish
        DELETE /api/v3/orders/cart/{item_id}/remove/
        """
        try:
            CartService.remove_from_cart(user=request.user, item_id=pk)
            cart = CartSelector.get_user_cart(request.user)
            return Response(CartSerializer(cart).data)
        except Exception as e:
            raise ValidationError({"detail": str(e)})

    @action(detail=True, methods=['patch'])
    def update_quantity(self, request, pk=None):
        """
        Miqdorni o'zgartirish
        PATCH /api/v3/orders/cart/{item_id}/update_quantity/
        {
            "quantity": 5
        }
        """
        quantity = request.data.get('quantity')
        if not quantity:
            raise ValidationError({"quantity": "Bu maydon majburiy"})

        try:
            CartService.update_quantity(
                user=request.user,
                item_id=pk,
                quantity=quantity
            )
            cart = CartSelector.get_user_cart(request.user)
            return Response(CartSerializer(cart).data)
        except Exception as e:
            raise ValidationError({"detail": str(e)})


# =========================================================
# ORDER VIEWSET (LOCKED-DOWN)
# =========================================================

class OrderViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):

    permission_classes = [permissions.IsAuthenticated, OrderPermission]
    pagination_class = OrderPagination

    # -----------------------------------------------------
    # SERIALIZER SWITCH
    # -----------------------------------------------------

    def get_serializer_class(self):
        if self.action == "create":
            return OrderCreateSerializer
        if self.action == "cancel":
            return OrderCancelSerializer
        if self.action == "change_status":
            return OrderStatusChangeSerializer
        return OrderSerializer

    # -----------------------------------------------------
    # QUERY
    # -----------------------------------------------------

    def get_queryset(self):
        user = self.request.user

        if user.role == "customer":
            return OrderSelector.for_customer(user)

        if user.role == "courier":
            return OrderSelector.for_courier(user)

        if user.role in {"operator", "admin"}:
            return OrderSelector.for_operator()

        return Order.objects.none()

    # -----------------------------------------------------
    # CREATE (checkout)
    # -----------------------------------------------------

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        try:
            order = serializer.save()

        except CartEmptyError:
            raise ValidationError({"detail": "Savatcha bo‘sh"})

        except InsufficientStockError as e:
            raise ValidationError({"detail": str(e)})

        return Response(
            OrderSerializer(order, context={"request": request}).data,
            status=status.HTTP_201_CREATED
        )

    # -----------------------------------------------------
    # CANCEL
    # -----------------------------------------------------

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        order = self.get_object()

        serializer = self.get_serializer(
            context={"order": order, "request": request}
        )

        try:
            serializer.save()

        except InvalidOrderStatusError as e:
            raise ValidationError({"detail": str(e)})

        return Response(
            OrderSerializer(order, context={"request": request}).data
        )

    # -----------------------------------------------------
    # CHANGE STATUS
    # -----------------------------------------------------

    @action(detail=True, methods=["post"], url_path="change-status")
    def change_status(self, request, pk=None):
        order = self.get_object()

        serializer = self.get_serializer(
            data=request.data,
            context={"order": order, "request": request}
        )
        serializer.is_valid(raise_exception=True)

        try:
            serializer.save()

        except InvalidOrderStatusError as e:
            raise ValidationError({"detail": str(e)})

        return Response(
            OrderSerializer(order, context={"request": request}).data
        )