from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'image', 'is_active')
        read_only_fields = ('id', 'email', 'username')
        
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'password', 'password2', 'image']
        extra_kwargs = {
            'password': {'write_only': True},
            'id': {'read_only': True},
            'email': {'required': True},
            'username': {'required': True},
            'image': {'required': True}
        }
        
    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({
                "password": "Password fields didn't match."
            })
        
        # Validate email
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({
                "email": "User with this email already exists."
            })
            
        # Validate username
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError({
                "username": "User with this username already exists."
            })
            
        return data
        
    def create(self, validated_data):
        # Remove password2 from the data
        validated_data.pop('password2')
        
        # Hash the password
        validated_data['password'] = make_password(validated_data['password'])
        
        # Create user instance
        user = User.objects.create(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password']
        )
        
        # Handle image if provided
        if 'image' in validated_data:
            user.image = validated_data['image']
            user.save()
            
        return user