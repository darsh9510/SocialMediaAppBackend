from rest_framework.pagination import PageNumberPagination
from django.http import JsonResponse
from post.models import Post
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied

def send_response(request, code, message, data):
 
    response = JsonResponse(data={'responseCode': code, 'responseMessage': message, 'responseData': data})
    response.status_code = code
    return response

def send_response_validation(request, code, message):
 
    response = JsonResponse(data={'responseCode': code, 'responseMessage': message})
    response.status_code = code
    return response

class Pagination(PageNumberPagination):
    page_size = 1

paginator = Pagination()

def paginatedData(paginator,data):

    returnData = {
        'count':paginator.page.paginator.count,
        'next_page':paginator.get_next_link(),
        'previous_page':paginator.get_previous_link(),
        'results':data
    }
    return returnData

def get_post_if_owner(post_id, user):
    post = get_object_or_404(Post, id=post_id)
    if post.poster != user:
        raise PermissionDenied('You are not the poster.')
    return post


