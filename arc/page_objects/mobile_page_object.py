# -*- coding: utf-8 -*-

import importlib

from arc.core.driver.driver_manager import DriverManager
from arc.page_objects.page_object import PageObject


class MobilePageObject(PageObject):
    def __new__(cls, driver_wrapper=None):
        if cls.__name__.startswith('Base'):
            __driver_wrapper = driver_wrapper if driver_wrapper else DriverManager.get_default_wrapper()
            __os_name = 'ios' if __driver_wrapper.is_ios_test() else 'android'
            __class_name = cls.__name__.replace('Base', __os_name.capitalize())
            try:
                return getattr(importlib.import_module(cls.__module__), __class_name)(__driver_wrapper)
            except AttributeError:
                __module_name = cls.__module__.replace('.base.', '.{}.'.format(__os_name))
                return getattr(importlib.import_module(__module_name), __class_name)(__driver_wrapper)
        else:
            return super(MobilePageObject, cls).__new__(cls)
