# -*- coding: utf-8 -*-

import logging


class CommonObject(object):

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.driver_wrapper = None

    def reset_object(self):
        pass

    @property
    def driver(self):
        return self.driver_wrapper.driver

    @property
    def config(self):
        return self.driver_wrapper.config

    @property
    def utils(self):
        return self.driver_wrapper.utils
