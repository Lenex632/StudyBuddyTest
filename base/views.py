from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.generic import DetailView, ListView

from .forms import RoomForm, UserForm, MyUserCreationForm
from .models import Room, Topic, Message, User


def login_page(request):
    page = 'login'

    if request.user.is_authenticated:
        return redirect('base:home')

    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User dose not exist')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('base:home')
        else:
            messages.error(request, 'Username or password dose not exist')

    context = {'page': page}
    return render(request, 'base/login_register.html', context)


def logout_page(request):
    logout(request)
    return redirect('base:home')


def registrate_page(request):
    form = MyUserCreationForm()

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('base:home')
        else:
            messages.error((request, 'An error occurred during registration'))

    context = {'form': form}
    return render(request, 'base/login_register.html', context)


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(
        Q(topic__name__contains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )
    all_topics = Topic.objects.all()
    topics = Topic.objects.all()[:5]
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))[:5]

    context = {
        'rooms': rooms,
        'topics': topics,
        'all_topics': all_topics,
        'room_count': room_count,
        'room_messages': room_messages,
    }
    return render(request, 'base/home.html', context)


def room_page(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()

    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('base:room', pk=room.id)

    context = {'room': room, 'room_messages': room_messages, 'participants': participants}
    return render(request, 'base/room.html', context)


class UserProfile(DetailView):
    template_name = 'base/profile.html'
    model = User

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.object
        context['rooms'] = self.object.room_set.all()
        context['room_messages'] = self.object.message_set.all()[:5]
        context['topics'] = Topic.objects.all()
        return context


@login_required(login_url='base:login')
def create_room(request):
    form = RoomForm()
    topics = Topic.objects.all()

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )
        return redirect('base:home')

    context = {'form': form, 'topics': topics}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='base:login')
def update_room(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    if request.user != room.host:
        return HttpResponse('Your not allowed here!!!')

    if request.method == 'POST':

        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('base:room', pk)

    context = {'form': form, 'topics': topics, 'room': room}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='base:login')
def delete_room(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('Your not allowed here!!!')

    if request.method == 'POST':
        room.delete()
        return redirect('base:home')

    return render(request, 'base/delete.html', {'obj': room})


@login_required(login_url='base:login')
def delete_message(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse('Your not allowed here!!!')

    if request.method == 'POST':
        message.delete()
        return redirect('base:room', message.room.id)

    return render(request, 'base/delete.html', {'obj': message})


@login_required(login_url='base:login')
def update_user(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('base:user-profile', pk=user.id)

    context = {'form': form}
    return render(request, 'base/update_user.html', context)


class TopicPage(ListView):
    model = Topic
    template_name = 'base/topics.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        q = self.request.GET.get('q') if self.request.GET.get('q') != None else ''
        topics = self.model.objects.filter(name__icontains=q)
        context = {'topics': topics}
        return context


class ActivityPage(ListView):
    model = Message
    template_name = 'base/activity.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        room_messages = self.model.objects.all()
        context = {'room_messages': room_messages}
        return context
