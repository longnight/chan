
A Django channels sample prj.
=============================


daphne chat.asgi:channel_layer --port 8888

python manage.py runworker


from helper.timelife_container import *
iii = KeysContainer()
iii.add('1')
iii.add('2')
iii.add('3')
iii.items()