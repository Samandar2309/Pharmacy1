from django.utils import timezone
from django.db.models import Prefetch
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import (
    DailyStats,
    ProductPerformance,
    CourierPerformance,
    SystemHealthLog,
)
from .serializers import (
    DailyStatsSerializer,
    ProductPerformanceSerializer,
    CourierPerformanceSerializer,
    SystemHealthLogSerializer,
    AdminDashboardSerializer,
    OperatorDashboardSerializer,
    CourierDashboardSerializer,
    CustomerDashboardSerializer,
)
from .permissions import (
    IsAdminRole,
    IsSystemHealthAdmin,
    IsOperatorRole,
    IsCourierRole,
    IsCustomerRole,
)
from .services import (
    get_admin_dashboard_overview,
    get_operator_dashboard_overview,
    get_courier_dashboard_overview,
    get_customer_dashboard_overview,
)


class AdminDashboardView(APIView):
    """Admin global dashboard."""

    permission_classes = [IsAuthenticated, IsAdminRole]

    def get(self, request):
        data = get_admin_dashboard_overview()
        serializer = AdminDashboardSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OperatorDashboardView(APIView):
    """Operator dashboard."""

    permission_classes = [IsAuthenticated, IsOperatorRole]

    def get(self, request):
        data = get_operator_dashboard_overview(operator=request.user)
        serializer = OperatorDashboardSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CourierDashboardView(APIView):
    """Courier dashboard."""

    permission_classes = [IsAuthenticated, IsCourierRole]

    def get(self, request):
        data = get_courier_dashboard_overview(courier=request.user)
        serializer = CourierDashboardSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CustomerDashboardView(APIView):
    """Customer dashboard."""

    permission_classes = [IsAuthenticated, IsCustomerRole]

    def get(self, request):
        data = get_customer_dashboard_overview(customer=request.user)
        serializer = CustomerDashboardSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DailyStatsListView(ListAPIView):
    """
    Sana bo‘yicha statistikani ko‘rish.
    ?from=2026-01-01&to=2026-01-31
    """

    serializer_class = DailyStatsSerializer
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get_queryset(self):
        queryset = DailyStats.objects.all().order_by("-date")

        date_from = self.request.query_params.get("from")
        date_to = self.request.query_params.get("to")

        if date_from:
            queryset = queryset.filter(date__gte=date_from)

        if date_to:
            queryset = queryset.filter(date__lte=date_to)

        return queryset


class TopProductsView(ListAPIView):
    """
    Eng ko‘p sotilgan mahsulotlar.
    ?limit=10
    """

    serializer_class = ProductPerformanceSerializer
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get_queryset(self):
        limit = int(self.request.query_params.get("limit", 10))

        return (
            ProductPerformance.objects
            .select_related("product")
            .order_by("-total_sold")[:limit]
        )


class TopCouriersView(ListAPIView):
    """
    Eng samarali kuryerlar.
    """

    serializer_class = CourierPerformanceSerializer
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get_queryset(self):
        limit = int(self.request.query_params.get("limit", 10))

        return (
            CourierPerformance.objects
            .select_related("courier")
            .order_by("-total_deliveries")[:limit]
        )


class SystemHealthLogView(ListAPIView):
    """
    Monitoring va loglar.
    """

    serializer_class = SystemHealthLogSerializer
    permission_classes = [IsAuthenticated, IsSystemHealthAdmin]
    pagination_class = None  # Agar global pagination bo‘lsa o‘chirmasa ham bo‘ladi

    def get_queryset(self):
        queryset = SystemHealthLog.objects.all()

        level = self.request.query_params.get("level")
        resolved = self.request.query_params.get("resolved")

        if level:
            queryset = queryset.filter(level=level)

        if resolved:
            queryset = queryset.filter(resolved=resolved.lower() == "true")

        return queryset.order_by("-created_at")