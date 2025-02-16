from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email']  # Removed password from response
        
class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)  # Add password confirmation
    
    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'password2']
        extra_kwargs = {
            'password': {'write_only': True},
            'id': {'read_only': True}
        }
        
    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({
                "password": "Password fields didn't match."
            })
        return data
        
    def create(self, validated_data):
        validated_data.pop('password2')  # Remove password2 before creating user
        user = User.objects.create(
            email=validated_data['email'],
            password=make_password(validated_data['password'])
        )
        return user