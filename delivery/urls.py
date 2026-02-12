from django.urls import path

from delivery.views import (
    OperatorDeliveryListView,
    AssignCourierView,
    CourierDeliveryListView,
    CourierDeliveryDetailView,
    CourierUpdateStatusView,
    CancelDeliveryView,
)

app_name = "delivery"

urlpatterns = [

    # =====================================================
    # OPERATOR / ADMIN
    # =====================================================

    # Yetkazishga tayyor deliverylar ro‘yxati
    path(
        "operator/deliveries/",
        OperatorDeliveryListView.as_view(),
        name="operator-delivery-list"
    ),

    # Buyurtmani kuryerga biriktirish
    path(
        "operator/orders/<int:order_id>/assign-courier/",
        AssignCourierView.as_view(),
        name="assign-courier"
    ),

    # Delivery bekor qilish (admin / operator)
    path(
        "operator/deliveries/<int:delivery_id>/cancel/",
        CancelDeliveryView.as_view(),
        name="cancel-delivery"
    ),


    # =====================================================
    # COURIER
    # =====================================================

    # Kuryerga biriktirilgan deliverylar
    path(
        "courier/deliveries/",
        CourierDeliveryListView.as_view(),
        name="courier-delivery-list"
    ),

    # Delivery tafsiloti
    path(
        "courier/deliveries/<int:delivery_id>/",
        CourierDeliveryDetailView.as_view(),
        name="courier-delivery-detail"
    ),

    # Delivery holatini yangilash (Yo‘lda / Yetkazildi)
    path(
        "courier/deliveries/<int:delivery_id>/update-status/",
        CourierUpdateStatusView.as_view(),
        name="courier-update-status"
    ),
]
