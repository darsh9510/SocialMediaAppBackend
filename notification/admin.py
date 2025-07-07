from django.contrib import admin
from unfold.paginator import InfinitePaginator
# Register your models here.
from .models import Notification
from unfold.admin import ModelAdmin, TabularInline

class NotificationInline(TabularInline):

    model = Notification
    per_page = 5
    fk_name = 'to_user'
    extra = 0
    fields = ['from_user','detail']
    readonly_fields = ['from_user','time','detail']
    verbose_name_plural = 'Recieved Notifications'
    can_delete = True
    def has_add_permission(self, request, obj=None):
        return False
    def has_change_permission(self, request, obj=None):
        return False

@admin.register(Notification)
class NotificationAdmin(ModelAdmin):

    list_per_page = 10
    list_display = [
        'to_user', 'from_user', 'time', 'detail'
    ]

    readonly_fields = list_display

    list_filter = ['time','detail']

    search_fields = [
        'to_user__username','from_user__username','detail'
    ]

    fieldsets = (
        (
            'Notification Details', {
                'fields': ('to_user','from_user','detail','time')
        }),
    )




