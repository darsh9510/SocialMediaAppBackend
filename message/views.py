from user.models import User
from notification.models import Notification
from message.models import Message
from .utils import send_response, send_response_validation
from .pagination import paginatedData
from notification.utils import send_notification
from .serializers import MessageSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Max
import jwt
from django.shortcuts import get_object_or_404

@api_view(['post'])
@permission_classes([IsAuthenticated])
def create_message(request):

    messageSender = request.user
    messageReciever = get_object_or_404(User,id=request.data.get('to_user'))
    data = dict(request.data)
    data['from_user'] = messageSender.id

    existingMessages = Message.objects.filter(
        ( Q(from_user = messageSender) & Q(to_user = messageReciever) ) |
        ( Q(from_user = messageReciever) & Q(to_user = messageSender) )
    )
    
    if existingMessages:
        data['thread'] = existingMessages[0].thread
        serializer = MessageSerializer(data = data, context = {'request':request})
        serializer.is_valid(raise_exception = True)
        newMessage = serializer.save()
        messageData = serializer.data

        unseenMessages = Message.objects.filter(to_user = messageSender, seen = False, thread = newMessage.thread)
        for message in unseenMessages:
            message.seen = True
            message.save()

        send_notification(newMessage, 'message', messageSender, messageReciever)
        return send_response(request, 200, message = 'Message Data', data = messageData)

    messageThread = Message.objects.aggregate(Max('thread'))['thread__max']
    if messageThread is None: 
        messageThread = 1
    else:
        messageThread += 1
    data['thread'] = messageThread
    serializer = MessageSerializer(data = data, context = {'request':request})
    serializer.is_valid(raise_exception = True)
    newMessage = serializer.save()
    messageData = serializer.data

    send_notification(newMessage, 'message', messageSender, messageReciever)
    return send_response(request, 200, message = 'Message Data', data = messageData)

@api_view(['post'])
@permission_classes([IsAuthenticated])
def update_message(request,messageID):

    currentUser = request.user
    requestedMessage = get_object_or_404(Message,id=messageID)

    serializer = MessageSerializer(instance = requestedMessage, data = request.data,context = {'request':request}, partial = True)
    serializer.is_valid(raise_exception = True)
    serializer.save()
    
    send_notification(requestedMessage, 'message', currentUser, requestedMessage.to_user)
    
    messageData = serializer.data

    unseenMessages = Message.objects.filter(to_user = currentUser, seen = False, thread = requestedMessage.thread)
    for message in unseenMessages:
        message.seen = True
        message.save()

    return send_response(request, 200, message = 'Message Data', data = messageData)

@api_view(['post'])
@permission_classes([IsAuthenticated])
def delete_message(request,messageID):

    currentUser = request.user
    requestedMessage = get_object_or_404(Message,id=messageID)

    if requestedMessage.from_user != currentUser:
        return send_response_validation(request, 403, message = 'user is not the sender')

    unseenMessages = Message.objects.filter(to_user = currentUser, seen = False, thread = requestedMessage.thread)
    for message in unseenMessages:
        message.seen = True
        message.save()
    
    requestedMessage.delete()
    return send_response_validation(request, 200, message = 'Message Deleted')

@api_view(['get'])
@permission_classes([IsAuthenticated])
def list_threads(request):
    
    currentUser = request.user
    querySet = Message.objects.filter(Q(from_user = currentUser) | Q(to_user = currentUser)).distinct('thread')

    unseenMessagesCount = 0
    threadData = []
    for thread in querySet:
        requestedUser = thread.to_user if thread.from_user == currentUser else thread.from_user
        data = {
            'thread': thread.thread,
            'current_user': currentUser.get_data(),
            'requested_user': requestedUser.get_data(),
            'unseen_messages_count': Message.objects.filter(to_user = currentUser, seen = False, thread = thread.thread).count()
        }
        unseenMessagesCount += data['unseen_messages_count']
        threadData.append(data)
    
    data = {
        'unseen_messages_count' : unseenMessagesCount,
        'threads' : paginatedData(request,threadData,pageSize=10)
    }
    return send_response(request, 200, message = 'List of user\'s threads', data = data)

@api_view(['get'])
@permission_classes([IsAuthenticated])
def get_thread(request,threadID):

    currentUser = request.user
    messagesData = Message.objects.filter(thread = threadID).values()
    
    if not messagesData:
        return send_response_validation(request, 400, message = 'no such thread')

    if int(messagesData[0]['from_user_id']) != currentUser.id and int(messagesData[0]['to_user_id']) != currentUser.id:
        return send_response(request, 400, message = 'not a participant of this thread')

    return send_response(request, 200, message = 'thread information', data = paginatedData(request,messagesData,pageSize=5))

@api_view(['get'])
@permission_classes([IsAuthenticated])
def search(request):

    currentUser = request.user
    searchQuery = request.data.get('search_query')

    messagesData = Message.objects.filter(Q(content__icontains = searchQuery) &(Q(to_user = currentUser) | Q(from_user = currentUser))).values()
    
    return send_response(request, 200, message = 'search results', data = paginatedData(request,messagesData,pageSize=5))

