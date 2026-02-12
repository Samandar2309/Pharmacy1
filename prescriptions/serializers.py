from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError

from .models import (
    Prescription,
    PrescriptionImage,
    PrescriptionItem
)
from .services import (
    create_prescription,
    approve_prescription,
    reject_prescription
)


class PrescriptionImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrescriptionImage
        fields = ['id', 'image', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']


class PrescriptionItemSerializer(serializers.ModelSerializer):
    dori_nomi = serializers.CharField(
        source='product.name',
        read_only=True
    )

    class Meta:
        model = PrescriptionItem
        fields = ['id', 'product', 'dori_nomi', 'quantity']


class PrescriptionCreateSerializer(serializers.ModelSerializer):
    # Fayllar alohida ListField sifatida olinadi
    rasmlar = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True
    )

    class Meta:
        model = Prescription
        fields = ['id', 'order', 'rasmlar']
        read_only_fields = ['id']

    # -------------------------
    # VALIDATION
    # -------------------------

    def validate_rasmlar(self, value):
        if not value:
            raise serializers.ValidationError(
                "Kamida bitta retsept rasmi yuklanishi kerak."
            )

        if len(value) > PrescriptionImage.MAX_IMAGES:
            raise serializers.ValidationError(
                f"Eng ko‘pi bilan {PrescriptionImage.MAX_IMAGES} ta rasm yuklash mumkin."
            )

        return value

    # -------------------------
    # CREATE (SERVICE-BASED)
    # -------------------------

    def create(self, validated_data):
        rasmlar = validated_data.pop('rasmlar')
        user = self.context['request'].user
        order = validated_data.get('order')

        try:
            prescription = create_prescription(
                user=user,
                order=order,
                images=[{'image': img} for img in rasmlar]
            )
        except DjangoValidationError as e:
            raise serializers.ValidationError(
                e.message_dict or e.messages
            )

        return prescription


class PrescriptionListSerializer(serializers.ModelSerializer):
    rasmlar = PrescriptionImageSerializer(
        many=True,
        read_only=True
    )
    dorilar = PrescriptionItemSerializer(
        many=True,
        read_only=True,
        source='items'
    )

    holat_nomi = serializers.CharField(
        source='get_status_display',
        read_only=True
    )

    class Meta:
        model = Prescription
        fields = [
            'id',
            'holat_nomi',
            'status',
            'rejection_reason',
            'created_at',
            'reviewed_at',
            'rasmlar',
            'dorilar'
        ]


class PrescriptionApproveSerializer(serializers.Serializer):

    def validate(self, attrs):
        prescription = self.context['prescription']
        if prescription.status != Prescription.Status.PENDING:
            raise serializers.ValidationError(
                'Faqat tekshirilayotgan retseptni tasdiqlash mumkin.'
            )
        return attrs

    def save(self, **kwargs):
        prescription = self.context['prescription']
        operator = self.context['request'].user

        try:
            approve_prescription(
                prescription=prescription,
                operator=operator
            )
        except DjangoValidationError as e:
            raise serializers.ValidationError(
                e.message_dict or e.messages
            )

        return prescription


class PrescriptionRejectSerializer(serializers.Serializer):
    rad_sababi = serializers.CharField(
        error_messages={
            'blank': 'Rad etish sababini kiritish majburiy.',
            'required': 'Rad etish sababi ko‘rsatilishi kerak.'
        }
    )

    def validate(self, attrs):
        prescription = self.context['prescription']
        if prescription.status != Prescription.Status.PENDING:
            raise serializers.ValidationError(
                'Faqat tekshirilayotgan retseptni rad etish mumkin.'
            )
        return attrs

    def save(self, **kwargs):
        prescription = self.context['prescription']
        operator = self.context['request'].user
        sabab = self.validated_data['rad_sababi']

        try:
            reject_prescription(
                prescription=prescription,
                operator=operator,
                reason=sabab
            )
        except DjangoValidationError as e:
            raise serializers.ValidationError(
                e.message_dict or e.messages
            )

        return prescription
