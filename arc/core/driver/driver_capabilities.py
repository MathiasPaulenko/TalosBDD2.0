# -*- coding: utf-8 -*-

import ast
import os
from configparser import NoSectionError
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium import webdriver

from arc.core import constants


def get_driver_capabilities(driver_name):
    if driver_name == constants.FIREFOX:
        return DesiredCapabilities.FIREFOX.copy()
    elif driver_name == constants.CHROME:
        return DesiredCapabilities.CHROME.copy()
    elif driver_name == constants.SAFARI:
        return DesiredCapabilities.SAFARI.copy()
    elif driver_name == constants.OPERA:
        return DesiredCapabilities.OPERA.copy()
    elif driver_name == constants.IEXPLORE:
        return DesiredCapabilities.INTERNETEXPLORER.copy()
    elif driver_name == constants.EDGE:
        return DesiredCapabilities.EDGE.copy()
    elif driver_name == constants.PHANTOMJS:
        return DesiredCapabilities.PHANTOMJS.copy()
    elif driver_name in (constants.ANDROID, constants.IOS, constants.IPHONE):
        return {}
    raise Exception(f"Unknown driver {driver_name}")


def add_driver_capabilities(capabilities, section, base_config):
    capabilities_type = {'Capabilities': 'server', 'AppiumCapabilities': 'Appium server'}
    try:
        for cap, cap_value in dict(base_config.config.items(section)).items():
            base_config.logger.debug(f"Added {capabilities_type[section]} capability: {cap} = {cap_value}")
            capabilities[cap] = cap_value if cap == 'version' else _convert_property_type(cap_value)
    except NoSectionError:
        pass


def _convert_property_type(value):
    if value in ('true', 'True'):
        return True
    elif value in ('false', 'False'):
        return False
    elif str(value).startswith('{') and str(value).endswith('}'):
        return ast.literal_eval(value)
    else:
        try:
            return int(value)
        except ValueError:
            return value


def add_firefox_arguments(options, base_config):
    try:
        for preference, preference_value in dict(base_config.config.items('FirefoxArguments')).items():
            preference_value = '={}'.format(preference_value) if preference_value else ''
            base_config.logger.debug(f"Added Firefox argument: {preference} = {preference_value}")
            options.add_argument('{}{}'.format(preference, _convert_property_type(preference_value)))
    except NoSectionError:
        pass


def create_firefox_profile(base_config):
    profile_directory = base_config.config.get_optional('Firefox', 'profile')

    if profile_directory:
        base_config.logger.debug(f"Using Firefox profile: {profile_directory}")

    profile = webdriver.FirefoxProfile(profile_directory=profile_directory)
    profile.native_events_enabled = True

    try:
        for preference, preference_value in dict(base_config.config.items('FirefoxPreferences')).items():
            base_config.logger.debug(f"Added Firefox preference: {preference} = {preference_value}")
            profile.set_preference(preference, _convert_property_type(preference_value))
        profile.update_preferences()
    except NoSectionError:
        pass

    try:
        for preference, preference_value in dict(base_config.config.items('FirefoxExtensions')).items():
            base_config.logger.debug(f"Added Firefox extension: {preference} = {preference_value}")

            profile.add_extension(preference_value)
    except NoSectionError:
        pass

    return profile


def create_chrome_options(base_config):
    options = webdriver.ChromeOptions()

    if base_config.config.getboolean_optional('Driver', 'headless'):
        base_config.logger.debug("Running Chrome in headless mode")
        options.add_argument('--headless')
        if os.name == 'nt':
            options.add_argument('--disable-gpu')

    add_chrome_options(options, 'prefs', base_config)
    add_chrome_options(options, 'mobileEmulation', base_config)
    add_chrome_arguments(options, base_config)

    return options


def add_chrome_options(options, option_name, base_config):
    options_conf = {
        'prefs': {
            'section': 'ChromePreferences',
            'message': 'preference'
        },
        'mobileEmulation': {
            'section': 'ChromeMobileEmulation',
            'message': 'mobile emulation option'
        }
    }

    option_value = dict()
    try:
        for key, value in dict(base_config.config.items(options_conf[option_name]['section'])).items():
            base_config.logger.debug("Added chrome %s: %s = %s", options_conf[option_name]['message'], key, value)
            option_value[key] = _convert_property_type(value)
        if len(option_value) > 0:
            options.add_experimental_option(option_name, option_value)
    except NoSectionError:
        pass


def add_chrome_arguments(options, base_config):
    try:
        for preference, preference_value in dict(base_config.config.items('ChromeArguments')).items():
            preference_value = '={}'.format(preference_value) if preference_value else ''
            base_config.logger.debug(f"Added Chrome argument: {preference} = {preference_value}")
            options.add_argument('{}{}'.format(preference, _convert_property_type(preference_value)))
    except NoSectionError:
        pass
