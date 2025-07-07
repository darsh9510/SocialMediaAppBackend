from django.contrib import admin
from .models import Comment, CommentLike
from unfold.paginator import InfinitePaginator
from unfold.admin import ModelAdmin, TabularInline

# Register your models here.

class CommentInline(TabularInline):
    model = Comment
    extra = 0
    per_page = 5
    fields = ['post','content','parent','commented_at']
    readonly_fields = ['post','parent','commented_at']
    can_delete = True
    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Comment)
class CommentAdmin(ModelAdmin):
    list_per_page = 10
    list_display = [
        'post', 'poster', 'content_preview',
        'commented_at', 'updated_at', 'parent',
        'comment_likes'
    ]

    list_filter = ['post','poster','parent']
    search_fields = ['post__title','poster__username','content']
    readonly_fields = ['post','poster']
    ordering = ['-updated_at']

    def comment_likes(self,obj):
        if obj and obj.pk:
            return CommentLike.objects.filter(comment = obj).count()
        return 0
    comment_likes.short_description = "Number of Comment Likes"

    def content_preview(seld,obj):
        return obj.content[:30] + "..." if len(obj.content) > 30 else obj.content
    content_preview.short_description = "Content Preview"

    fieldsets = (
        (
            'Comment Details', {
                'fields': ('post','poster','content')
            }
        ),
    )

