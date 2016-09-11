# -*- coding: utf-8 -*-
import json
from datetime import datetime
from django.http import HttpResponse
from django.db import transaction
from django.shortcuts import render, redirect
import haikunator
from channels import Group
from models import Room
from channels import Channel


def index(request):
    message = {'ABC': 123}
    Channel('test_channel').send(message)
    return HttpResponse("Hello, world. You're at the polls index.")


def new_room(request):
    """
    Randomly create a new room, and redirect to it.
    """
    new_room = None
    while not new_room:
        with transaction.atomic():
            label = haikunator.haikunate()
            if Room.objects.filter(label=label).exists():
                continue
            new_room = Room.objects.create(label=label)
    return redirect(chat_room, label=label)


def chat_room(request, label):
    # If the room with the given label doesn't exist, automatically create it
    # upon first visit (a la etherpad).
    room, created = Room.objects.get_or_create(label=label)

    # We want to show the last 50 messages, ordered most-recent-last
    messages = reversed(room.messages.order_by('-timestamp')[:50])

    print('^'*10 + 'Wellcome to chat room: %s' % label + '^'*10)

    return render(request, "chat/room.html", {
        'room': room,
        'messages': messages,
    })
