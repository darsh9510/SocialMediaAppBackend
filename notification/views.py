from post.models import Post, Reactions
from comment.models import Comment
from message.models import Message
from notification.models import Notification
from .utils import send_response, send_response_validation
from .pagination import paginator, paginatedData
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import jwt
from django.shortcuts import get_object_or_404


@api_view(['get'])
@permission_classes([IsAuthenticated])
def get_notification(request):

    currentUser = request.user
    querySet = Notification.objects.filter(to_user = currentUser).order_by('-time').values()
    notificationData = paginator.paginate_queryset(querySet,request)

    for data in notificationData:
        notification = Notification.objects.get(id=data['id'])
        notification.read= True
        notification.save()
        
        notificationType = data['detail'].split(':')
        notificationType[1] = int(notificationType[1])

        if notificationType[0]=='post' and Post.objects.filter(id = notificationType[1]).exists():  
            data['post'] = Post.objects.filter(id=int(type[1])).values()[0]
        
        if (notificationType[0]=='post comment' or notificationType[0]=='comment like' or notificationType[0]=='reply') and Comment.objects.filter(id = notificationType[1]).exists():
            data['comment'] = Comment.objects.filter(id=int(type[1])).values()[0]
        
        if notificationType[0]=='reaction' and Reactions.objects.filter(id = notificationType[1]).exists():
            data['reaction'] = Reactions.objects.filter(id = notificationType[1]).values()[0]
        
        if notificationType[0]=='message' and Message.objects.filter(id = notificationType[1]).exists():
            data['message'] = Message.objects.filter(id = notificationType[1]).values()[0]

    return send_response(request, 200, message = 'notifications', data = paginatedData(paginator, notificationData))


