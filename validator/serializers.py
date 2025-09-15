from rest_framework import serializers
from .models import EmailValidationResult

class ValidateEmailsSerializer(serializers.Serializer):
    emails = serializers.ListField(
        child=serializers.EmailField(),
        allow_empty=False,
        max_length=10000
    )

class EmailValidationResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailValidationResult
        fields = "__all__"