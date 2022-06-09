# -*- coding: utf-8 -*-
import logging

from arc.core.behave.env_utils import (
    utils_after_scenario,
    utils_after_all,
    utils_before_all,
    utils_before_feature,
    utils_after_feature,
    utils_before_scenario
)

try:
    from behave_pytest.hook import install_pytest_asserts
except ImportError:
    def install_pytest_asserts():
        pass


def before_all(context):
    install_pytest_asserts()
    utils_before_all(context)

    context.logger = logging.getLogger(__name__)
    context.logger.debug(f"the core before all actions have been executed correctly")


def before_feature(context, feature):
    utils_before_feature(context, feature)
    context.logger.debug(f"the core before feature actions have been executed correctly")


def before_scenario(context, scenario):
    utils_before_scenario(context, scenario)
    context.logger.debug(f"the core before scenario actions have been executed correctly")


def after_scenario(context, scenario):
    utils_after_scenario(context, scenario, scenario.status)
    context.logger.debug(f"the core after scenario actions have been executed correctly")


def after_feature(context, feature):
    utils_after_feature(context, feature)
    context.logger.debug(f"the core after feature actions have been executed correctly")


def after_all(context):
    utils_after_all(context)
    context.logger.debug(f"the core after all actions have been executed correctly")


