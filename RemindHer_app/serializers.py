from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    confirmPassword = serializers.CharField(write_only=True)  # ✅ Add confirmPassword field

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'password', 'confirmPassword', 'status']
        extra_kwargs = {'password': {'write_only': True}}  # ✅ Ensure password is not returned

    def validate(self, data):
        # ✅ Check if password and confirmPassword match
        password = data.get('password')
        confirmPassword = data.get('confirmPassword')

        if password != confirmPassword:
            raise serializers.ValidationError({"confirmPassword": "Passwords do not match."})

        return data

    def create(self, validated_data):
        validated_data.pop('confirmPassword')  # ✅ Remove confirmPassword before saving
        validated_data['status'] = 'Active'  # ✅ Ensure user is active
        user = User(
            name=validated_data['name'],
            email=validated_data['email'],
            status='Active'
        )
        user.set_password(validated_data['password'])  # ✅ Hash password properly
        user.save()
        return user
