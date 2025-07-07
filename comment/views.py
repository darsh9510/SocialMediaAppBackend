from post.models import Post
from comment.models import Comment, CommentLike
from notification.models import Notification
from .utils import nested_comments, send_response, send_response_validation
from .pagination import paginator, paginatedData
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
import jwt
from django.shortcuts import get_object_or_404
from .serializers import CommentSerializer
from notification.utils import send_notification


@api_view(['post'])
@permission_classes([IsAuthenticated])
def create_comment(request):

    currentUser = request.user
    post = get_object_or_404(Post, id = request.data.get('post_id'))
    data = dict(request.data)
    data['poster'] = currentUser.id
    data['post'] = post.id
    data['parent'] = None
    dataValidator = CommentSerializer(data = data)
    dataValidator.is_valid(raise_exception = True)
    postComment = dataValidator.save()
    requestedPost = get_object_or_404(Post, id = request.data.get('post_id'))
    send_notification(postComment, 'post comment', currentUser, requestedPost.poster)
    commentData = dataValidator.data
    
    return send_response(request, 201, message = 'commented successfully', data = commentData)

@api_view(['post'])
@permission_classes([IsAuthenticated])
def update_comment(request,commentID):

    requestedComment = get_object_or_404(Comment,id=commentID)
    serializer = CommentSerializer(instance = requestedComment, data = request.data, context = {'request' : request}, partial = True)
    serializer.is_valid(raise_exception = True)
    serializer.save()
    return send_response_validation(request, 200, message = 'Comment updated successfully')

# either make the values null, or delete entirely.
@api_view(['post'])
@permission_classes([IsAuthenticated])
def delete_comment(request,commentID):

    currentUser = request.user
    requestedComment = get_object_or_404(Comment,id = commentID)

    if requestedComment.poster != currentUser:
        return send_response_validation(request, 403, message = 'user is not the sender')

    childs = Comment.objects.filter(parent = requestedComment)
    for child in childs:
        child.parent = requestedComment.parent
        child.save()

    requestedComment.delete()
    return send_response_validation(request, 200, message = 'Comment deleted successfully')

@api_view(['post'])
@permission_classes([IsAuthenticated])
def reply_comment(request,commentID):
    
    currentUser = request.user
    data = dict(request.data)
    parentComment = get_object_or_404(Comment, id = commentID)
    data['post'] = parentComment.post.id
    data['poster'] = parentComment.poster.id
    data['parent'] = parentComment.id
    serializer = CommentSerializer(data = data, context = {'request':request})
    serializer.is_valid(raise_exception = True)
    replyComment = serializer.save()
    send_notification(replyComment, 'reply', currentUser, parentComment.poster)
    return send_response(request, 201, message = 'Replied to the comment created', data = serializer.data)

@api_view(['post'])
@permission_classes([IsAuthenticated])
def like_unlike_comment(request,commentID):
    
    currentUser = request.user
    requestedComment = get_object_or_404(Comment,id=commentID)

    try:
        commentLike = CommentLike.objects.get(comment=requestedComment,user=currentUser)
        commentLike.delete()
        return send_response_validation(request, 200, message = 'current status: unliked')
    except CommentLike.DoesNotExist:
        CommentLike.objects.create(comment = requestedComment, user = currentUser)
        send_notification(requestedComment, 'comment like', currentUser, requestedComment.poster)

        return send_response_validation(request, 200, message = 'current status: liked')

@api_view(['get'])
@permission_classes([AllowAny])
def get_comment(request,commentID):

    currentUser = request.user
    requestedComment = get_object_or_404(Comment,id = commentID)
    commentData = nested_comments(requestedComment, current_depth = 0, all_childs = True, user = currentUser)
    return send_response(request, 200, message = 'comment fetched', data = commentData)


@api_view(['get'])
@permission_classes([IsAuthenticated])
def search(request):

    searchQuery = request.data.get('search_query')
    querySet = Comment.objects.filter(content__icontains = searchQuery).order_by('-updated_at').values()
    commentsData = paginator.paginate_queryset(querySet,request)
    return send_response(request, 200, message = 'Search Results', data = paginatedData(paginator,commentsData))

