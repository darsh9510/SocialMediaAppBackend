from user.models import User, UserRelation
from post.models import Post, PostLike, Reactions
from comment.models import Comment, CommentLike
from message.models import Message
from .serializers import UserSerializer
from .utils import send_response, send_response_validation, get_user_data, is_blocked
from notification.utils import send_notification
from .pagination import generalPaginator, paginatedData
from notification.models import Notification
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q
from rest_framework_simplejwt.tokens import RefreshToken
from operator import itemgetter
from django.core.mail import send_mail
import random
from datetime import datetime
from django.conf import settings
from django.shortcuts import get_object_or_404

@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    
    serializer = UserSerializer(data = request.data)
    serializer.is_valid(raise_exception = True)
    serializer.save()
    return send_response(request,201,message = 'User created',data = serializer.data)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_otp(request):

    userEmail = request.data.get('email')
    requestedUser = get_object_or_404(User,email=userEmail)

    otp = random.randint(100000,999999)
    requestedUser.otp = otp
    requestedUser.save()

    emailSubject = 'Your OTP for Login'
    emailMessage = f'Your OTP is: {otp}'
    fromEmail = settings.EMAIL_HOST_USER
    send_mail(emailSubject, emailMessage, fromEmail, [userEmail])

    return send_response_validation(request,200,'otp sent')

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):

    userEmail = request.data.get('email')
    otp = request.data.get('otp')

    requestedUser = get_object_or_404(User, email = userEmail)

    if otp==requestedUser.otp:
        requestedUser.otp = None

        refreshToken = RefreshToken.for_user(requestedUser)
        accessToken = str(refreshToken.access_token)
        refreshToken = str(refreshToken)

        requestedUser.login_time = datetime.now()
        requestedUser.save()
        return send_response(
            request,
            code = 200,
            message = 'logged in',
            data = {
                'refresh':refreshToken,
                'access':accessToken,
            }
        )

    return send_response(request,code = 400,message = 'invalid otp')

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def log_out(request):
    try:
        refreshToken = request.data.get('refresh')
        token = RefreshToken(refreshToken)
        token.blacklist()
        user = request.user
        user.logout_time = datetime.now()
        user.last_login = user.login_time
        user.login_time = None
        user.save()
        return send_response_validation(request,205,'logged out')
    except Exception as e:
        return send_response_validation(request,400,'already logged out')

@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):

    userEmail = request.data.get('email')
    requestedUser = get_object_or_404(User,email = userEmail)
    subject = 'Update Password on this link'
    message = 'Update link: http://127.0.0.1:8000/user/update_password/'
    fromEmail = settings.EMAIL_HOST_USER
    send_mail(subject, message, fromEmail, [userEmail])
    return send_response_validation(request, 200, message = 'sent the password updation link via mail')

@api_view(['POST'])
@permission_classes([AllowAny])
def update_forgot_password(request):

    userPassword = request.data.get('password')
    userEmail = request.data.get('email')
    requestedUser = get_object_or_404(User, email = userEmail)

    serializer = UserSerializer(instance = requestedUser,data = {'username':requestedUser.username ,'password':userPassword},partial = True)
    serializer.is_valid(raise_exception = True)
    serializer.save()
    
    return send_response_validation(request, 200, message = 'password updated')

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_password(request):

    oldPassword = request.data.get('old_password')
    newPassword = request.data.get('new_password')

    currentUser = request.user
    if currentUser.check_password(oldPassword):
        serializer = UserSerializer(instance = currentUser,data = {'username':currentUser.username, 'password':newPassword},partial = True)
        serializer.is_valid(raise_exception = True)
        return send_response_validation(request, 200, message = 'password changed')
    
    return send_response_validation(request, 400, message = 'wrong old password')

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_profile(request):

    user = request.user
    serializer = UserSerializer(instance = user, data = request.data, partial = True)
    serializer.is_valid(raise_exception = True)
    return send_response_validation(request, 200, message = 'information updated')

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def follow(request,userID):

    currentUser = request.user
    requestedUser = get_object_or_404(User,id=userID)
    requestedUserRelation = UserRelation.objects.get(id=userID)
    
    blockedOrNot = is_blocked(request, currentUser, requestedUser)
    if blockedOrNot:
        return blockedOrNot
    
    blockedOrNot = is_blocked(request, requestedUser, currentUser)
    if blockedOrNot:
        return blockedOrNot
    
    if requestedUserRelation.followers.all().filter(id=currentUser.id).exists():
        return send_response_validation(request, 200, message = 'already follows')

    if Notification.objects.filter(to_user = requestedUser, from_user = currentUser, detail = f'follow request:{currentUser.id}').exists():
        return send_response_validation(request, 200, message = 'already sent the request')

    send_notification(currentUser, 'follow request', currentUser, requestedUser)
    return send_response_validation(request, 200, message = 'follow request sent')

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unfollow(request,userID):

    currentUser = request.user
    requestedUser = get_object_or_404(User,id=userID)
    requestedUserRelation = UserRelation.objects.get(id=requestedUser.id)
    userRelation = UserRelation.objects.get(id=currentUser.id)
    
    if userRelation.followers.all().filter(id=currentUser.id):
        requestedUserRelation.followers.remove(currentUser)
        userRelation.following.remove(requestedUser)
        return send_response_validation(request, 200, message = 'unfollowed')
    
    return send_response_validation(request, 400, message = 'already not following')

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def decide_follow_request(request):

    currentUser = request.user

    if request.data.get('notification_id') is None or request.data.get('approve') is None:
        return send_response_validation(request, 200, message = 'fields are empty')
    
    notificationID = int(request.data.get('notification_id'))
    followNotification = get_object_or_404(Notification, id = int(notificationID))

    if followNotification.to_user.id != currentUser.id:
        return send_response_validation(request, 400, message = 'user is not the reciever of this notification')

    fromUser = followNotification.from_user

    userRelation = UserRelation.objects.get(id=currentUser.id)
    fromUserRelation = UserRelation.objects.get(id=fromUser.id)
    
    if request.data.get('approve') == True:
        userRelation.followers.add(fromUser)
        fromUserRelation.following.add(currentUser)
        userRelation.save()
        fromUserRelation.save()
        followNotification.delete()
        return send_response_validation(request, 200, message = 'request accepted')
    
    userRelation.save()
    fromUserRelation.save()
    followNotification.delete()

    return send_response_validation(request, 200, message = 'request rejected')

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def block_user(request,userID):
    
    currentUser = request.user
    
    requestedUser = get_object_or_404(User,id=userID)
    
    userRelation = UserRelation.objects.get(id=currentUser.id)
    blockedOrNot = is_blocked(request, requestedUser, currentUser)
    if blockedOrNot:
        return blockedOrNot
    
    userRelation.blocked_users.add(requestedUser)
    
    return send_response_validation(request, 200, message = 'blocked successfully')

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unblock_user(request,userID):
    
    currentUser = request.user
    requestedUser = get_object_or_404(User,id=userID)
    userRelation = UserRelation.objects.get(id=currentUser.id)
    
    if not userRelation.blocked_users.filter(id=requestedUser.id).exists():
        return send_response_validation(request, 200, message = 'not blocked by the user')
    
    userRelation.blocked_users.remove(requestedUser)
    
    return send_response_validation(request, 200, message = 'unblocked successfully')

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def blocked_users_list(request):
    
    currentUser = request.user
    userRelation = UserRelation.objects.get(id=currentUser.id)

    querySet = userRelation.blocked_users.all()
    paginatedQuerySet = generalPaginator.paginate_queryset(querySet,request)
    serializer = UserSerializer(paginatedQuerySet, many = True)
    return send_response(
        request, 
        200, 
        message = f'{currentUser.username} blocked list', 
        data = generalPaginator.get_paginated_response(serializer.data).data
    )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_user(request,userID):
    
    currentUser = request.user
    requestedUser = get_object_or_404(User,id=userID)
    return send_response(request, 200, message = f'{requestedUser.username} data', data = get_user_data(currentUser,requestedUser))

@api_view(['GET'])
@permission_classes([AllowAny])
def get_user_posts(request,userID):
    
    currentUser = request.user
    requestedUser = get_object_or_404(User,id=userID)
    
    postsData = Post.objects.filter(poster=requestedUser).values()
    for post in postsData:
        post['is_liked'] = False
        post['user_reaction'] = None

        if not currentUser.is_authenticated:
            continue
        
        userReaction = Reactions.objects.filter(user=currentUser, post__id=post['id']).values()
        if userReaction:
            post['user_reaction'] = userReaction[0]['reaction']

        try:
            if PostLike.objects.filter(post__id=post['id'],id=currentUser.id).exists():
                post['is_liked'] = True
        except PostLike.DoesNotExist:
            pass

    return send_response(request, 200, message = f'{requestedUser.username} data', data = paginatedData(request,postsData,pageSize=1))

@api_view(['GET'])
@permission_classes([AllowAny])
def get_user_comments(request,userID):
    
    currentUser = request.user
    requestedUser = get_object_or_404(User,id=userID)

    commentsData = Comment.objects.filter(poster=requestedUser).values()

    for i in range(len(commentsData)):
        commentsData[i]['is_liked'] = False
        if currentUser.is_authenticated and CommentLike.objects.filter(comment__id=commentsData[i]['id'],user=currentUser).exists():
            commentsData[i]['is_liked'] = True

    return send_response(request, 200, message = f'{requestedUser.username} data', data = paginatedData(request,commentsData,pageSize=5))

@api_view(['GET'])
@permission_classes([AllowAny])
def list_followers(request,userID):
    
    requestedUser = get_object_or_404(User,id=userID)
    requestedUserRelation = UserRelation.objects.get(user=requestedUser)
    
    querySet = requestedUserRelation.followers.all()
    paginatedQuerySet = generalPaginator.paginate_queryset(querySet,request)
    serializer = UserSerializer(paginatedQuerySet, many = True)
    return send_response(
        request, 
        200, 
        message = f'{request.user.username} followers list', 
        data = generalPaginator.get_paginated_response(serializer.data).data
    )

@api_view(['GET'])
@permission_classes([AllowAny])
def list_followings(request,userID):
    
    requestedUser = get_object_or_404(User,id=userID)
    requestedUserRelation = UserRelation.objects.get(user=requestedUser)
    
    querySet = requestedUserRelation.following.all()
    paginatedQuerySet = generalPaginator.paginate_queryset(querySet,request)
    serializer = UserSerializer(paginatedQuerySet, many = True)
    return send_response(
        request, 
        200, 
        message = f'{request.user.username} followings list', 
        data = generalPaginator.get_paginated_response(serializer.data).data
    )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_users(request):
    
    querySet = User.objects.all().order_by('username')
    paginatedQuerySet = generalPaginator.paginate_queryset(querySet,request)
    serializer = UserSerializer(paginatedQuerySet, many = True)
    paginated_response = generalPaginator.get_paginated_response(serializer.data)
    return send_response(
        request, 
        200, 
        message = 'users list', 
        data = paginated_response.data
    )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_loggedin_user(request):
    
    return send_response(
        request,
        200,
        message = 'Current User data',
        data = get_user_data(request.user,request.user)
    )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_user(request):

    currentUser = request.user
    try:
        refreshToken = request.data.get('refresh')
        token = RefreshToken(refreshToken)
        token.blacklist()
    except Exception as e:
        return send_response_validation(request, 400, message = str(e))

    userName = currentUser.username
    messages = Message.objects.filter(from_user = currentUser)
    for message in messages:
        message.delete()
    currentUser.delete()
    
    return send_response_validation(request, 200, message = f'{userName} deleted successfully')

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search(request):

    currentUser = request.user
    searchQuery = request.data.get('search_query')
    
    usersData = User.objects.filter(
        Q(username__icontains = searchQuery) |
        Q(first_name__icontains = searchQuery) |
        Q(last_name__icontains = searchQuery) |
        Q(bio__icontains = searchQuery)
    ).values('id', 'username', 'first_name', 'last_name', 'bio')

    try:
        userRelation = UserRelation.objects.get(id=currentUser.id)
    except UserRelation.DoesNotExist:
        pass

    for user in usersData:
        user['is_following'] = False
        if userRelation.following.filter(id=user['id']).exists():
            user['is_following'] = True
    
    usersData = sorted(usersData, key = itemgetter('is_following'),reverse=True)
    return send_response(request, 200, message = 'Search results', data = paginatedData(request,usersData,pageSize=10))


