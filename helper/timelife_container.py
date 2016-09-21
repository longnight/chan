# -*- coding: utf-8 -*-
from django.core.cache import cache
from collections import deque
from uuid import uuid4

CACHE_KEY = 'k_que'
LIFETIME = 40
MAX = 5


class KeysContainer(object):
    """
    实现一个FIFO容器，其中的item保存于cache并带有lifetime.
    """

    def get_k_que_cache(self):
        return cache.get_or_set(
            CACHE_KEY, deque(list(), maxlen=MAX), LIFETIME*30)

    def items(self):
        v_list = list()
        k_que = self.get_k_que_cache()
        if k_que:
            for key in k_que:
                v = cache.get(key)
                if v:
                    v_list.insert(0, v)
        return v_list

    def add(self, *items):
        for item in items:
            new_k = uuid4()
            cache.set(new_k, item, LIFETIME)
            k_que = self.get_k_que_cache()
            k_que.append(new_k)
            cache.set(CACHE_KEY, k_que, LIFETIME*30)
        return

    def clear(self):
        cache.delete(CACHE_KEY)
        return
