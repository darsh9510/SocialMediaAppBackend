from rest_framework import serializers
from .models import Comment
from user.models import User
from post.models import Post

class CommentSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Comment
        fields = '__all__'

    def create(self, data):
        parent = user = post = None
        poster_data = data.get('poster')
        if isinstance(poster_data, User):
            user = poster_data
        else:
            try:
                user_id = int(poster_data) if poster_data else None
                user = User.objects.get(id=user_id)
            except (ValueError, TypeError, User.DoesNotExist) as e:
                raise serializers.ValidationError(f"Invalid poster: {e}")
        
        post_data = data.get('post')
        if isinstance(post_data,Post):
            post = post_data
        else:
            try:
                post_id = int(post_data) if post_data else None
                post = Post.objects.get(id = post_id)
            except (ValueError, TypeError, Post.DoesNotExist) as e:
                raise serializers.ValidationError(f"Invalid Post: {e}")
        
        parent_data = data.get('parent')
        print(parent_data)
        if isinstance(parent_data,Comment):
            parent = parent_data
        else:
            parent_id = int(parent_data) if parent_data else None
            if parent_id is None:
                parent = None
            else:
                try:
                    parent = Comment.objects.get(id = parent_id)
                except (ValueError, TypeError, Comment.DoesNotExist) as e:
                    raise serializers.ValidationError(f"Invalid Parent: {e}")
        print(parent)
        comment = Comment.objects.create(
            post = post,
            poster = user,
            content = data.get('content'),
            parent = parent
        )
        comment.save()
        return comment
    
    def update(self, instance, data):

        user = self.context['request'].user
        if instance.poster.id != user.id:
            raise serializers.ValidationError('User is not the poster of this comment')

        content = data.get('content')
        if content:
            instance.content = content
        instance.save()
        return instance

