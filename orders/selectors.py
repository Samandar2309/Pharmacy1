from orders.models import Order, Cart


class CartSelector:

    @staticmethod
    def get_user_cart(user):
        return (
            Cart.objects
            .select_related("user")
            .prefetch_related("items", "items__product")
            .get_or_create(user=user)[0]
        )


class OrderSelector:

    BASE_QS = (
        Order.objects
        .select_related("user", "courier")
        .prefetch_related("items", "items__product", "history")
    )

    @staticmethod
    def for_customer(user):
        return OrderSelector.BASE_QS.filter(user=user)

    @staticmethod
    def for_courier(user):
        return OrderSelector.BASE_QS.filter(courier=user)

    @staticmethod
    def for_operator():
        return OrderSelector.BASE_QS
