import re
import json
from time import sleep
import logging
from django.http import HttpResponse
from channels import Group
from channels.handler import AsgiHandler
from channels.sessions import channel_session
from channels.auth import (
    http_session_user, channel_session_user, channel_session_user_from_http
    )
from .models import Room


log = logging.getLogger(__name__)


def index(message):
    # Make standard HTTP response - access ASGI path attribute directly
    response = HttpResponse(
        "Hello world! You asked for %s" % message.content['path'])
    # Encode that response into message format (ASGI)
    for chunk in AsgiHandler.encode_response(response):
        message.reply_channel.send(chunk)


@channel_session
def ws_connect(message):
    # Extract the room from the message. This expects message.path to be of the
    # form /chat/{label}/, and finds a Room if the message path is applicable,
    # and if the Room exists. Otherwise,
    # bails (meaning this is a some othersort
    # of websocket). So, this is effectively a version of _get_object_or_404.
    try:
        prefix, label = message['path'].decode('ascii').strip('/').split('/')
        if prefix != 'chat':
            log.debug('invalid ws path=%s', message['path'])
            return
        room = Room.objects.get(label=label)
    except ValueError:
        log.debug('invalid ws path=%s', message['path'])
        return
    except Room.DoesNotExist:
        log.debug('ws room does not exist label=%s', label)
        return

    log.debug(
        'chat connect room=%s client=%s:%s',
        room.label, message['client'][0], message['client'][1])

    # Need to be explicit about the channel layer so that
    # testability works This may be a FIXME?
    Group('chat-'+label, channel_layer=message.channel_layer).add(
        message.reply_channel)

    # import pdb; pdb.set_trace()

    Group(
        message.channel_session.session_key,
        channel_layer=message.channel_layer).add(
        message.reply_channel)

    print('iam coming to ws connect~~' + '-'*100)

    message.channel_session['room'] = room.label


@channel_session
def ws_receive(message):
    # Look up the room from the channel session, bailing if it doesn't exist
    try:
        label = message.channel_session['room']
        room = Room.objects.get(label=label)
    except KeyError:
        log.debug('no room in channel_session')
        return
    except Room.DoesNotExist:
        log.debug('recieved message, buy room does not exist label=%s', label)
        return

    # Parse out a chat message from the content text, bailing if it doesn't
    # conform to the expected message format.
    try:
        data = json.loads(message['text'])
    except ValueError:
        log.debug("ws message isn't json text=%s", message['text'])
        return

    if set(data.keys()) != set(('handle', 'message')):
        log.debug("ws message unexpected format data=%s", data)
        return

    if data:
        log.debug(
            'chat message room=%s handle=%s message=%s',
            room.label, data['handle'], data['message'])
        m = room.messages.create(**data)

        # import pdb; pdb.set_trace()
        m
        print('we are at ws receive!!!!' + '*'*100)
        print(data['message'])
        # print(message.channel_layer)

        # See above for the note about Group
        Group('chat-'+label, channel_layer=message.channel_layer).send(
            {'text': json.dumps(data)})

        sleep(5)

        Group(
            message.channel_session.session_key,
            channel_layer=message.channel_layer).send(
            {'text': json.dumps(
                {'message': "you just typed in %s" % data['message'],
                 'handle': 'system say:'})})

        # if 'myxxoo' in data['message']:
        #     Group('xxoo', channel_layer=message.channel_layer).send(
        #         {'text': json.dumps(
        #             {'message': "you're in xxoo!", 'handle': 'system say'})})


@channel_session
def ws_disconnect(message):
    try:
        label = message.channel_session['room']
        room = Room.objects.get(label=label)
        room

        print('we disssssconnnect yet.' + '/'*100)

        Group('chat-'+label, channel_layer=message.channel_layer).discard(
            message.reply_channel)

        Group(
            message.channel_session.session_key,
            channel_layer=message.channel_layer).discard(
            message.reply_channel)

        # Group('xxoo', channel_layer=message.channel_layer).discard(
        #     message.reply_channel)

    except (KeyError, Room.DoesNotExist):
        pass
