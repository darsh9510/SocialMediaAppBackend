from django.contrib import admin
from post.models import Post, PostLike, Reactions
from comment.admin import CommentInline
from unfold.paginator import InfinitePaginator
from unfold.admin import ModelAdmin, TabularInline
from django.forms.models import BaseInlineFormSet

class PostInline(TabularInline):
    model = Post
    per_page = 5
    extra = 0
    fields = ['title','description', 'posted_at', 'updated_at']
    readonly_fields = ['posted_at','updated_at']
    can_delete = True
    def has_add_permission(self, request, obj=None):
        return False

class ReactionInline(TabularInline):
    model = Reactions
    per_page = 5
    extra = 0
    fields = ['reaction', 'post']
    readonly_fields = fields
    verbose_name_plural = 'Reactions'
    can_delete = True
    def has_add_permission(self, request, obj=None):
        return False
    

@admin.register(Post)
class PostAdmin(ModelAdmin):
    list_per_page = 10
    list_display = [
        'poster', 'title_preview', 'description_preview',
        'posted_at', 'updated_at', 'post_likes_count'
    ]

    list_filter = ['poster__username',]

    search_fields = [
        'title', 'description', 'poster__username'
    ]

    ordering = ['-posted_at']

    def post_likes_count(self,obj):
        if obj and obj.pk:
            return PostLike.objects.filter(post=obj).count()
        return 0
    post_likes_count.short_description = "Post Likes Count"

    def title_preview(self,obj):
        return obj.title[:30] + "..." if len(obj.title) > 30 else obj.title
    title_preview.short_description = "Title Preview"

    def description_preview(self,obj):
        return obj.description[:30] + "..." if len(obj.description) > 30 else obj.description
    description_preview.short_description = "Description Preview"

    inlines = [CommentInline, ReactionInline]

    fieldsets = (
        (
            'Post Details' , {
                'fields' : ('poster', 'title', 'description',),
            }
        ),
    )
