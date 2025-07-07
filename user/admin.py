from django.contrib import admin
from user.models import User, UserRelation
from post.admin import PostInline, ReactionInline
from comment.admin import CommentInline
from message.admin import SentMessageInline, RecievedMessageInline
from notification.admin import NotificationInline
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from unfold.admin import ModelAdmin
from unfold.admin import StackedInline
from unfold.paginator import InfinitePaginator

# Register your models here.

class UserRelationInline(StackedInline):
    model = UserRelation
    extra = 0
    fields = ['followers_count', 'following_count', 'blocked_count']
    readonly_fields = ['followers_count', 'following_count', 'blocked_count']
    can_delete = False
    
    def followers_count(self, obj):
        if obj and obj.pk:
            return obj.followers.count()
        return 0
    followers_count.short_description = "Number of Followers"
    
    def following_count(self, obj):
        if obj and obj.pk:
            return obj.following.count()
        return 0
    following_count.short_description = "Number of Following"
    
    def blocked_count(self, obj):
        if obj and obj.pk:
            return obj.blocked_users.count()
        return 0
    blocked_count.short_description = "Number of Blocked"

@admin.register(User)
class UserAdmin(ModelAdmin):
    list_per_page = 10
    list_display = [
        'username', 'email', 'first_name', 'last_name', 
        'is_active', 'followers_count_display', 'following_count_display',
        'last_login', 'date_joined', 'bio_preview'
    ]
    
    list_filter = [
        'is_active', 'is_staff', 'is_superuser', 
        'date_joined', 'last_login', 'login_time'
    ]
    
    search_fields = [
        'username', 'email', 'first_name', 'last_name', 'bio'
    ]
    
    ordering = ['-date_joined']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('username', 'email', 'first_name', 'last_name', ),
        }),
        ('Additional Information', {
            'fields': ('bio', 'otp', 'login_time', 'logout_time'),
        }),
    )
    
    readonly_fields = ['date_joined', 'last_login', 'login_time', 'logout_time']
    
    add_fieldsets = (
        ('Basic Information', {
            'fields': ('username','email', 'first_name', 'last_name'),
        }),
        ('Additional Information', {
            'fields': ('bio'),
        }),
    )
    
    inlines = [UserRelationInline, 
               PostInline, 
               ReactionInline,
               CommentInline,
               SentMessageInline,
               RecievedMessageInline,
               NotificationInline,
            ]
    def bio_preview(self, obj):
        if obj.bio:
            return obj.bio[:30] + "..." if len(obj.bio) > 30 else obj.bio
        return "No bio"
    bio_preview.short_description = "Bio"
    
    def followers_count_display(self, obj):
        try:
            relation = obj.userrelation
            return relation.followers.count()
        except UserRelation.DoesNotExist:
            return 0
    followers_count_display.short_description = "Followers"
    
    def following_count_display(self, obj):
        try:
            relation = obj.userrelation
            return relation.following.count()
        except UserRelation.DoesNotExist:
            return 0
    following_count_display.short_description = "Following"

    def last_login_display(self,obj):
        if obj and obj.pk and obj.last_login:
            return obj.last_login.strftime("%Y-%m-%d %H:%M")
        return "Never"
    last_login_display.short_description = "Last Login"
    
    actions = ['activate_users', 'deactivate_users', 'clear_otp', 'create_user_relations']

    def activate_users(self,request,queryset):
        updated = queryset.update(is_active = True)
        self.message_user(request, f'{updated} users were successfully activated.')
    activate_users.short_description = "Activate Users"

    def deactivate_users(self,request,queryset):
        updated = queryset.update(is_active = False)
        self.message_user(request, f'{updated} users were successfully deactivated.')
    deactivate_users.short_description = "Deactivate Users"

    def clear_otp(self,request,queryset):
        updated = queryset.update(otp = None)
        self.message_user(request, f'{updated} users\' otp were successfully cleared.')
    clear_otp.short_description = "Clear OTP"

    def create_user_relations(self,request,queryset):
        queryset.order_by('id')
        updated = 0
        for user in queryset:
            relation, created = UserRelation.objects.get_or_create(user = user)
            if created:
                updated+=1
        self.message_user(request, f'{updated} users were successfully created.')
    create_user_relations.short_description = "Create UserRelation"


@admin.register(UserRelation)
class UserRelationAdmin(ModelAdmin):
    list_per_page = 10
    
    list_display = [
        'user', 'followers_count', 'following_count', 'blocked_count'
    ]
    
    list_filter = ['user__is_active', 'user__date_joined']
    
    search_fields = [
        'user__username', 'user__email', 'user__first_name', 'user__last_name'
    ]
    
    ordering = ['user__username']
    
    filter_horizontal = ['followers', 'following', 'blocked_users']

    def followers_count(self,obj):
        return obj.followers.count()
    followers_count.short_description = "Followers count"

    def following_count(self,obj):
        return obj.following.count()
    following_count.short_description = "Followings count"

    def blocked_count(self,obj):
        return obj.blocked_users.count()
    blocked_count.short_description = "Blocked users count"

    fieldsets = (
        ('User Information', {
            'fields': ('user',),
        }),
        ('Relationships', {
            'fields': ('followers', 'following', 'blocked_users'),
            'description': 'Manage user relationships.'
        }),
    )

    actions = ['clear_blocked_users',]

    def clear_blocked_users(self,request,queryset):
        for userRelation in queryset:
            userRelation.blocked_users.clear()
        self.message_user(request,f'Cleared blocked list of {queryset.count()} users successfully.')
    clear_blocked_users.short_description = "Clear Blocked List"

