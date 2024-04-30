
# -*- coding: utf-8 -*-

"""
@author: takeEasy9
@description: singleton container
@version: 1.0.0
@since: 2024/4/30 19:31
"""

from typing import TypeVar, Type

T = TypeVar('T')


class _SingletonContainer:
    def __init__(self) -> None:
        self.__singletonMap = {}
        self.__singletonFactoryMap = {}

    def register(self, singleton_type, instance=None) -> None:
        if instance is None:
            self.__singletonFactoryMap[singleton_type.__name__] = lambda: singleton_type()
        else:
            assert (isinstance(instance, singleton_type))
            self.__singletonMap[singleton_type.__name__] = instance

    def get_instance(self, singleton_type: Type[T]) -> T:
        class_name = singleton_type.__name__
        assert (class_name in self.__singletonMap.keys()
                or class_name in self.__singletonFactoryMap.keys())
        if class_name not in self.__singletonMap.keys():
            self.__singletonMap[class_name] = self.__singletonFactoryMap[class_name]()
        return self.__singletonMap[class_name]


SingletonContainer = _SingletonContainer()
