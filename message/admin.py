from django.contrib import admin
from .models import Message
from unfold.paginator import InfinitePaginator
# Register your models here.
from unfold.admin import ModelAdmin, TabularInline

class SentMessageInline(TabularInline):
    model = Message
    fk_name = 'from_user'
    per_page = 5
    extra = 0
    fields = ['from_user','to_user','content','thread','first_sent','seen']
    verbose_name_plural = 'Sent Messages'
    readonly_fields = fields
    can_delete = True
    def has_add_permission(self, request, obj=None):
        return False
    
class RecievedMessageInline(TabularInline):
    model = Message
    fk_name = 'to_user'
    per_page = 5
    extra = 0
    fields = ['from_user','to_user','content','thread','first_sent','seen']
    readonly_fields = ['from_user','to_user','content','thread','first_sent']
    verbose_name_plural = 'Recieved Messages'
    can_delete = True
    def has_add_permission(self, request, obj=None):
        return False
    

@admin.register(Message)
class MessageAdmin(ModelAdmin):

    list_per_page = 10

    list_display = [
        'from_user', 'to_user', 'content_preview',
        'thread', 'first_sent', 'last_updated', 'seen'
    ]
    
    readonly_fields = ['first_sent','last_updated','thread','to_user','from_user']

    list_filter = [
        'from_user', 'to_user', 'thread', 'seen'
    ]

    search_fields = [
        'from_user__username', 'to_user__username', 'content', 'thread'
    ]

    ordering = ['-last_updated']

    def content_preview(self,obj):
        return obj.content[:30] + '...' if len(obj.content)>30 else obj.content
    content_preview.short_description = "Message Preview"

    fieldsets = (
        (
            'Message Details', {
                'fields': ('from_user','to_user', 'content', 'first_sent', 'last_updated', 'seen')
            }
        ),
    )

