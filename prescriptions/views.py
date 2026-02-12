from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404

from .models import Prescription
from .serializers import (
    PrescriptionCreateSerializer,
    PrescriptionListSerializer,
    PrescriptionApproveSerializer,
    PrescriptionRejectSerializer
)
from .permissions import (
    IsAdminOrOperator,
    PrescriptionObjectPermission
)

MSG_APPROVED = "Retsept muvaffaqiyatli tasdiqlandi."
MSG_REJECTED = "Retsept rad etildi."


class PrescriptionViewSet(viewsets.GenericViewSet):
    """
    Retseptlar bilan ishlash uchun API.
    Real dorixona product darajasida.
    """

    permission_classes = [IsAuthenticated, PrescriptionObjectPermission]

    # MUHIM: rasm upload uchun
    parser_classes = [MultiPartParser, FormParser]

    # -------------------------
    # QUERYSET
    # -------------------------
    def get_queryset(self):
        return (
            Prescription.objects
            .select_related('user', 'order', 'reviewed_by')
            .prefetch_related('images', 'items__product')
        )

    def create(self, request):
        serializer = PrescriptionCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        prescription = serializer.save()

        return Response(
            PrescriptionListSerializer(prescription).data,
            status=status.HTTP_201_CREATED
        )

    def list(self, request):
        queryset = self.get_queryset()

        if not request.user.is_staff:
            queryset = queryset.filter(user=request.user)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = PrescriptionListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = PrescriptionListSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        prescription = get_object_or_404(self.get_queryset(), pk=pk)
        self.check_object_permissions(request, prescription)

        serializer = PrescriptionListSerializer(prescription)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAdminOrOperator],
        url_path='pending'
    )
    def pending(self, request):
        queryset = self.get_queryset().filter(
            status=Prescription.Status.PENDING
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = PrescriptionListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = PrescriptionListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAdminOrOperator],
        url_path='approve'
    )
    def approve(self, request, pk=None):
        prescription = get_object_or_404(self.get_queryset(), pk=pk)
        self.check_object_permissions(request, prescription)

        serializer = PrescriptionApproveSerializer(
            data={},
            context={
                'request': request,
                'prescription': prescription
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                'id': prescription.id,
                'status': prescription.status,
                'holat_nomi': prescription.get_status_display(),
                'reviewed_at': prescription.reviewed_at,
                'xabar': MSG_APPROVED
            },
            status=status.HTTP_200_OK
        )

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAdminOrOperator],
        url_path='reject'
    )
    def reject(self, request, pk=None):
        prescription = get_object_or_404(self.get_queryset(), pk=pk)
        self.check_object_permissions(request, prescription)

        serializer = PrescriptionRejectSerializer(
            data=request.data,
            context={
                'request': request,
                'prescription': prescription
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                'id': prescription.id,
                'status': prescription.status,
                'holat_nomi': prescription.get_status_display(),
                'reviewed_at': prescription.reviewed_at,
                'xabar': MSG_REJECTED
            },
            status=status.HTTP_200_OK
        )
