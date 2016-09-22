# -*- coding: utf-8 -*-

from collections import deque
from uuid import uuid4
from django.core.cache import cache
from django.conf import settings


class KeysContainer(object):
    """
    实现一个FIFO容器，其中的item保存于cache并带有lifetime.
    """

    def __init__(
            self,
            cache_key=settings.CACHE_KEY, cache=cache,
            lifetime=settings.LIFETIME, max_num=settings.MAXITEMS
            ):
        pass
        self.cache_key = cache_key
        self.cache = cache
        self.lifetime = lifetime
        self.max_num = max_num

    def get_k_que_cache(self):
        return self.cache.get_or_set(
            self.cache_key, deque(list(), maxlen=self.max_num))

    def items(self):
        v_list = list()
        k_que = self.get_k_que_cache()
        if k_que:
            for key in k_que:
                v = self.cache.get(key)
                if v:
                    v_list.append(v)
        return v_list.reverse()

    def add(self, *items):
        for item in items:
            new_k = uuid4()
            self.cache.set(new_k, item, self.lifetime)
            k_que = self.get_k_que_cache()
            k_que.append(new_k)
            self.cache.set(self.cache_key, k_que)
        return

    def clear(self):
        self.cache.delete(self.cache_key)
        return
