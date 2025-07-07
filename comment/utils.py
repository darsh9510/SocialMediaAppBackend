from post.models import Post
from comment.models import Comment, CommentLike
from rest_framework.pagination import PageNumberPagination
from django.http import JsonResponse

class Pagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 20

paginator = Pagination()

def send_response(request, code, message, data):
 
    response = JsonResponse(data={'responseCode': code, 'responseMessage': message, 'responseData': data})
    response.status_code = code
    return response

def send_response_validation(request, code, message):
 
    response = JsonResponse(data={'responseCode': code, 'responseMessage': message})
    response.status_code = code
    return response

def nested_comments(comment,current_depth,all_childs,user):

    if current_depth>3 and (not all_childs): return 'view single comment to get more replies'

    commentData = Comment.objects.filter(id=comment.id).values()[0]
    commentData['likes'] = CommentLike.objects.filter(comment__id = commentData['id']).count()
    commentData['is_liked'] = False
    if CommentLike.objects.filter(comment=comment,user=user).exists():
        commentData['is_liked'] = True

    temp = Comment.objects.filter(parent=comment)

    commentData['num_childs'] = len(temp)
    for i in range(len(temp)):
        commentData[f'child {i+1} data'] = nested_comments(temp[i],current_depth+1,all_childs,user)

    return commentData

def paginatedData(paginator,data):

    returnData = {
        'count':paginator.page.paginator.count,
        'next_page':paginator.get_next_link(),
        'previous_page':paginator.get_previous_link(),
        'results':data
    }
    return returnData
