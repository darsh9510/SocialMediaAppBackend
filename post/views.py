from post.models import Post, PostLike, Reactions
from comment.models import Comment
from comment.views import nested_comments
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q
import jwt
from django.shortcuts import get_object_or_404
from .serializers import ReactionSerializer, PostSerializer
from .utils import send_response, send_response_validation
from .pagination import paginatedData
from notification.utils import send_notification

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_post(request):
    
    data = dict(request.data)
    data['poster'] = request.user.id
    dataValidator = PostSerializer(data = data)
    dataValidator.is_valid(raise_exception = True)
    userPost = dataValidator.save()
    postData = Post.objects.filter(id=userPost.id).values()[0]
    
    return send_response(request, 200, message = 'post created', data = postData)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_post(request,postID):

    requestedPost = get_object_or_404(Post,id=postID)
    dataValidator = PostSerializer(instance = requestedPost, data = request.data, context = {'request':request}, partial = True)
    dataValidator.is_valid(raise_exception = True)
    dataValidator.save()
    return send_response_validation(request, 200, message = 'post updated')

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_post(request,postID):

    currentUser = request.user
    requestedPost = get_object_or_404(Post,id=postID)

    if requestedPost.poster.id==currentUser.id:
        requestedPost.delete()
        return send_response_validation(request, 200, message = 'successfully deleted')

    return send_response_validation(request, 403, message = 'not the poster')

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def like_unlike_post(request,postID):
    
    currentUser = request.user
    requestedPost = get_object_or_404(Post,id=postID)

    try:
        postLike = PostLike.objects.get(post=requestedPost,user=currentUser)
        postLike.delete()
        return send_response_validation(request, 200, message = 'current status: unliked')
    except PostLike.DoesNotExist:
        PostLike.objects.create(
            post = requestedPost,
            user = currentUser
        )
        send_notification(requestedPost, 'post', request.user, requestedPost.user)
        return send_response_validation(request, 200, message = 'current status: liked')

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def post_reaction(request,postID):

    currentUser = request.user
    requestedPost = get_object_or_404(Post,id=postID)
    data = dict(request.data)
    data['user'] = int(currentUser.id)

    try:
        currentReaction = Reactions.objects.get(user=currentUser,post=requestedPost)
    except Reactions.DoesNotExist:
        reactionValidator = ReactionSerializer(data = data)
        reactionValidator.is_valid(raise_exception = True)
        newReaction = reactionValidator.save()
        send_notification(newReaction, 'reaction', currentUser, requestedPost.poster)
        return send_response_validation(request, 200, message = 'reacted to the post')

    reactionValidator = ReactionSerializer(instance = currentReaction, data = data)
    reactionValidator.is_valid(raise_exception = True)
    reactionValidator.save()
    send_notification(currentReaction, 'reaction', currentUser, requestedPost.poster)

    return send_response_validation(request, 200, message = 'reaction changed')

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_reaction(request,postID):

    currentUser = request.user
    requestedPost = get_object_or_404(Post,id=postID)

    try:
        userReaction = Reactions.objects.get(post=requestedPost,user=currentUser)
        userReaction.delete()
        return send_response_validation(request, 200, message = 'Reaction removed')
    except Reactions.DoesNotExist:
        return send_response_validation(request, 400, message = 'No reaction found')


@api_view(['GET'])
@permission_classes([AllowAny])
def get_post(request,postID):

    requestedPost = get_object_or_404(Post,id = postID)
    currentUser = request.user
    
    postData = Post.objects.filter(id=requestedPost.id).values()[0]
    
    postData['reactions_count'] = Reactions.objects.filter(post__id=requestedPost.id).count()
    postData['user_reaction'] = None
    postData['likes_count'] = PostLike.objects.filter(post=requestedPost).count()
    postData['is_liked'] = False
    postData['comments_count'] = Comment.objects.filter(post__id=requestedPost.id).count()
    
    if currentUser.is_authenticated:
        userReaction = Reactions.objects.filter(Q(user__id=currentUser.id) & Q(post__id=requestedPost.id)).values()
        if userReaction:
            postData['user_reaction'] = userReaction[0]['reaction']
        if PostLike.objects.filter(post = requestedPost, user = currentUser).exists():
            postData['is_liked'] = True

    return send_response(request, 200, message = 'Post data fetched', data = postData)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_post_reactions(request,postID):

    requestedPost = get_object_or_404(Post,id = postID)
    querySet = Reactions.objects.filter(post__id=requestedPost.id).values()
    return send_response(request, 200, message = 'Post data fetched', data = paginatedData(request,querySet,pageSize=10))

@api_view(['GET'])
@permission_classes([AllowAny])
def get_post_likes(request,postID):

    requestedPost = get_object_or_404(Post,id = postID)
    querySet = PostLike.objects.filter(post=requestedPost).values()
    return send_response(request, 200, message = 'Post data fetched', data = paginatedData(request,querySet,pageSize=10))

@api_view(['GET'])
@permission_classes([AllowAny])
def get_post_comments(request,postID):

    currentUser = request.user
    requestedPost = get_object_or_404(Post,id = postID)
    querySet = Comment.objects.filter(post=requestedPost, parent__isnull=True)
    nested = [nested_comments(comment, current_depth=0, all_childs = False, user = currentUser) for comment in querySet]
    return send_response(request, 200, message = 'Post data fetched', data = paginatedData(request,nested,pageSize=5))

@api_view(['GET'])
@permission_classes([AllowAny])
def list_posts(request):

    currentUser = request.user
    postsData = Post.objects.all().values()
    for post in postsData:
        post['is_liked'] = False
        post['reaction'] = None
        if currentUser.is_authenticated:
            if PostLike.objects.filter(post__id=post['id'],user__id=currentUser.id).exists():
                post['is_liked'] = True
            userReaction = Reactions.objects.filter(post__id=post['id'],user__id=currentUser.id)
            if userReaction:
                post['reaction'] = userReaction[0]['reaction']
    
    return send_response(request, 200, message = 'List of Posts', data = paginatedData(request,postsData,pageSize=1))

@api_view(['GET'])
@permission_classes([AllowAny])
def search(request):

    searchQuery = request.data.get('search_query')
    querySet = Post.objects.filter(Q(title__icontains = searchQuery) | Q(description__icontains = searchQuery)).values()
    return send_response(request, 200, message = 'Result of Search Query', data = paginatedData(request,querySet,pageSize=1))

