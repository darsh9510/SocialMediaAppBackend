from django.http import JsonResponse
from user.models import UserRelation
from rest_framework import serializers
import re


def send_response(request, code, message, data):
 
    response = JsonResponse(data={'responseCode': code, 'responseMessage': message, 'responseData': data})
    response.status_code = code
    return response

def send_response_validation(request, code, message):
 
    response = JsonResponse(data={'responseCode': code, 'responseMessage': message})
    response.status_code = code
    return response

def validate_password(value):
    errors = [
        'Password must contain at least one numerical',
        'Password must contain at least one small case',
        'Password must contain at least one upper case',
        'Password must contain at least one special character'
    ]
    pattern = '^(?=.*[0-9])+(?=.*[a-z])+(?=.*[A-Z])+(?=.*[\W])+'
    if not re.match(pattern,value):
        raise serializers.ValidationError(errors)
    return value

def validate_password_username(data):
    username = data['username']
    password = data['password']
        
    if username == password:
        raise serializers.ValidationError('Password is same as Username')
    
    pattern = f'.*{password}.*'
    m = re.match(pattern,username)
    if m is not None and m[0]:
        raise serializers.ValidationError('Password is contained in Username')
    
    pattern = f'.*{username}.*'
    m = re.match(pattern,password)
    if m is not None and m[0]:
        raise serializers.ValidationError('Username is contained in Password')
    
    return data

def get_user_data(user, requestedUser):

    requestedUserData = requestedUser.get_data()
    data = {
        'user_details': requestedUserData,
        'profile_picture_base64encoded':None
    }

    if user.id!=requestedUser.id:
        data['is_blocked'] = False
        data['is_following'] = False

    if user.is_authenticated and user.id!=requestedUser.id:
        userRelation = UserRelation.objects.get(user=user)
        if userRelation.blocked_users.filter(id=requestedUser.id).exists():
            data['is_blocked'] = True
        if userRelation.following.filter(id=requestedUser.id).exists():
            data['is_following']=True

    return data

def is_blocked(request, user1, user2):

    if user1.id == user2.id:
        return send_response_validation(request, 400, message = 'cannot block yourself')
    
    user2Relation = UserRelation.objects.get(user = user2)
    if user2Relation.blocked_users.filter(id = user1.id).exists():
        return send_response_validation(request, 200, message = f'{user1.username} is blocked by {user2.username}')
    return None