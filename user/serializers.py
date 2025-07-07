from rest_framework import serializers
from email_validator import validate_email, EmailNotValidError
from .models import User, UserRelation
from .utils import validate_password, validate_password_username
from datetime import datetime

class UserSerializer(serializers.Serializer):

    username = serializers.CharField(max_length = 20)
    password = serializers.CharField(max_length = 20, min_length = 8, write_only = True, validators = [validate_password])
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length = 20)
    last_name = serializers.CharField(max_length = 20, required = False)
    bio = serializers.CharField(max_length = 200, required = False)

    def to_internal_value(self,data):
        fields = set(self.fields)
        cleanedData = {k:v for k,v in data.items() if k in fields}
        return super().to_internal_value(cleanedData)
    
    def create(self,validated_data):
        userName = validated_data.get('username')
        email = validated_data.get('email')
        firstName = validated_data.get('first_name')
        lastName = validated_data.get('last_name')
        bio = validated_data.get('bio')
        password = validated_data.get('password')

        user = User.objects.create(
            username = userName,
            email = email,
            first_name = firstName,
            last_name = lastName,
            bio = bio,
            date_joined = datetime.now()
        )
        user.set_password(password)
        user.save()
        UserRelation.objects.create(user = user)
        return user

    def update(self,instance,validated_data):
        
        userName = validated_data.get('username')
        firstName = validated_data.get('first_name')
        lastName = validated_data.get('last_name')
        bio = validated_data.get('bio')
        password = validated_data.get('password')

        if userName is not None:
            instance.username = userName
            instance.save()
        if firstName is not None:
            instance.first_name = firstName
            instance.save()
        if lastName is not None:
            instance.last_name = lastName
            instance.save()
        if bio is not None:
            instance.bio = bio
            instance.save()
        if password is not None:
            userName = instance.username
            data = {
                'username': userName,
                'password': password
            }
            validate_password_username(data)
            instance.set_password(password)
            instance.save()
        return instance

    def validate_email(self,value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Already registered with this email')
        try:
            validate_email(value,check_deliverability=True)
            return value
        except EmailNotValidError as e:
            raise serializers.ValidationError(str(e))

    def validate_username(self,value):
        if self.instance is not None:
            return value
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('This username is taken')
        return value

    def validate(self,data):
        if self.instance is None:
            return validate_password_username(data)
        return self.update(self.instance,data)
        
