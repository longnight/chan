# -*- coding: utf-8 -*-
from django.core.cache import cache
from collections import deque

LIFETIME = 5    
MAX = 10


class TimelifeContainer(object):

    k_list = ['msg_%d' % i for i in range(1, MAX+1)]
    
    def __init__(self, cache=cache):
        self.k_q = deque(
            [k if cache.get(k) for k in TimelifeContainer.k_list ], 
            maxlen=MAX
            )

    def items(self):
        return

    def add(self, item):
        self.q.append()

