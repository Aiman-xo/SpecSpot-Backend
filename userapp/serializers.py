from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import Customer


class CustomerSerializer(ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    signup_date = serializers.DateField(read_only=True)
    status = serializers.CharField(read_only=True)

    class Meta:
        model = Customer
        fields = ['name', 'email', 'status', 'password',
                  'confirm_password', 'signup_date']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError('password must be same')
        
        try:
            validate_password(data['password'])
        except DjangoValidationError as e:
            raise serializers.ValidationError({"password": e.messages})
        return data

    def validate_email(self, value):
        # FIX 4: Custom duplicate email check (better DRF error message)
        if Customer.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered.")
        return value

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')

        user = Customer.objects.create_user(
            password=password,
            status="Active",
            ** validated_data
        )
        return user


class CustomerProfileSerializer(ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'name', 'email', 'status', 'is_staff','is_active']
        read_only_fields = ["email", "is_staff",'is_active']


class ResetPasswordSerializer(serializers.Serializer):
    reset_session = serializers.CharField()
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        
        try:
            validate_password(data['password'])
        except DjangoValidationError as e:
            raise serializers.ValidationError({"password": e.messages})
        return data
    

    
    