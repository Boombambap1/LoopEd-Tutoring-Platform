from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Max
from .models import Conversation, Message

User = get_user_model()

@login_required
def inbox(request):
    conversations = Conversation.objects.filter(
        participants=request.user
    ).annotate(
        latest_message_time=Max('messages__created_at')
    ).order_by('-latest_message_time')
    
    return render(request, 'messaging/inbox.html', {
        'conversations': conversations
    })

@login_required
def conversation_detail(request, conversation_id):
    conversation = get_object_or_404(
        Conversation, 
        id=conversation_id, 
        participants=request.user
    )
    
    conversation.messages.filter(
        ~Q(sender=request.user), 
        is_read=False
    ).update(is_read=True)
    
    messages_list = conversation.messages.order_by('created_at')
    other_participant = conversation.get_other_participant(request.user)
    
    return render(request, 'messaging/conversation.html', {
        'conversation': conversation,
        'messages': messages_list,
        'other_participant': other_participant,
    })

@login_required
def send_message(request, conversation_id):
    if request.method == 'POST':
        conversation = get_object_or_404(
            Conversation, 
            id=conversation_id, 
            participants=request.user
        )
        
        content = request.POST.get('content', '').strip()
        if content:
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=content
            )
            conversation.save()
            
        # ✅ FIX: add namespace
        return redirect('messaging:conversation_detail', conversation_id=conversation_id)
    
    return redirect('messaging:inbox')   # ✅ also needs namespace

@login_required
def start_conversation(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    
    if other_user == request.user:
        messages.error(request, "You can't start a conversation with yourself.")
        return redirect('messaging:inbox')   # ✅ add namespace
    
    existing_conversation = Conversation.objects.filter(
        participants=request.user
    ).filter(
        participants=other_user
    ).first()
    
    if existing_conversation:
        # ✅ FIX: add namespace
        return redirect('messaging:conversation_detail', conversation_id=existing_conversation.id)
    
    conversation = Conversation.objects.create()
    conversation.participants.add(request.user, other_user)
    
    initial_message = request.POST.get('message', '').strip()
    if initial_message:
        Message.objects.create(
            conversation=conversation,
            sender=request.user,
            content=initial_message
        )
    
    # ✅ FIX: add namespace
    return redirect('messaging:conversation_detail', conversation_id=conversation.id)

@login_required
def delete_conversation(request, conversation_id):
    conversation = get_object_or_404(
        Conversation, 
        id=conversation_id, 
        participants=request.user
    )
    
    conversation.participants.remove(request.user)
    
    if conversation.participants.count() == 0:
        conversation.delete()
    
    messages.success(request, 'Conversation deleted.')
    return redirect('messaging:inbox')   # ✅ add namespace


