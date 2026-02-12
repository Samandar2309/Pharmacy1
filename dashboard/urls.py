from django.urls import path
from .views import (
    AdminDashboardView,
    OperatorDashboardView,
    CourierDashboardView,
    CustomerDashboardView,
    DailyStatsListView,
    TopProductsView,
    TopCouriersView,
    SystemHealthLogView,
)

app_name = "dashboard"

urlpatterns = [
    # Role-based dashboards
    path("admin/", AdminDashboardView.as_view(), name="admin-dashboard"),
    path("operator/", OperatorDashboardView.as_view(), name="operator-dashboard"),
    path("courier/", CourierDashboardView.as_view(), name="courier-dashboard"),
    path("customer/", CustomerDashboardView.as_view(), name="customer-dashboard"),

    # Daily statistics
    path("daily-stats/", DailyStatsListView.as_view(), name="daily-stats"),

    # Product analytics
    path("top-products/", TopProductsView.as_view(), name="top-products"),

    # Courier analytics
    path("top-couriers/", TopCouriersView.as_view(), name="top-couriers"),

    # Monitoring & logs
    path("system-health/", SystemHealthLogView.as_view(), name="system-health"),
]