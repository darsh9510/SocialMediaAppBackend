from rest_framework import serializers
from .models import Post, PostLike, Reactions
from user.models import User, UserRelation
from django.shortcuts import get_object_or_404

class ReactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Reactions
        fields = '__all__'

    def create(self,data):
        user_data = data.get('user')
        if isinstance(user_data,User):
            user = user_data
        else:
            user = User.objects.get(id = int(user_data))
        
        post_data = data.get('post')
        if isinstance(post_data,Post):
            post = post_data
        else:
            post = Post.objects.get(id = int(post_data))

        reaction = Reactions.objects.create(
            post = post,
            user = user,
            reaction = data.get('reaction')
        )
        reaction.save()
        return reaction

    def update(self,instance,validated_data):
        if instance.reaction == validated_data.get('reaction'):
            raise serializers.ValidationError('Already reacted with the same reaction')
        instance.reaction = validated_data.get('reaction')
        instance.save()
        return instance


class PostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = '__all__'
    
    def create(self,data):
        poster_data = data.get('poster')
        if isinstance(poster_data, User):
            user = poster_data
        else:
            try:
                user_id = int(poster_data) if poster_data else None
                user = User.objects.get(id=user_id)
            except (ValueError, TypeError, User.DoesNotExist) as e:
                raise serializers.ValidationError(f"Invalid poster: {e}")
        
        post = Post.objects.create(
            poster=user,
            title=data.get('title'),
            description=data.get('description')
        )
        return post
    def update(self,instance,data):
        
        user = self.context['request'].user
        if instance.poster.id != user.id:
            raise serializers.ValidationError('User is not the poster of this post')
        
        title = data.get('title')
        description = data.get('description')

        if title:
            instance.title = title
        if description:
            instance.description = description
        instance.save()
        return instance

