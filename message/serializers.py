from rest_framework import serializers
from .models import Message
from user.models import User

class MessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = '__all__'
    
    def create(self,data):

        sender_data = data.get('from_user')
        reciever_data = data.get('to_user')

        if isinstance(sender_data,User):
            sender = sender_data
        else:
            sender_id = int(sender_data)
            sender = User.objects.get(id = sender_id)

        if isinstance(reciever_data,User):
            reciever = reciever_data
        else:
            reciever_id = int(reciever_data)
            reciever = User.objects.get(id = reciever_id)

        message = Message.objects.create(
            from_user = sender,
            to_user = reciever,
            content = data.get('content'),
            thread = data.get('thread')
        )
        message.save()
        return message
    
    def update(self,instance,data):

        if self.context['request'].user.id != instance.from_user.id:
            raise serializers.ValidationError('user is not the sender')
        
        content = data.get('content')
        if content:
            instance.content = content
        instance.seen = False
        instance.save()
        return instance

