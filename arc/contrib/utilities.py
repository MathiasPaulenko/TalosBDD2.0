# -*- coding: utf-8 -*-
import logging
import os
import re
import time
from datetime import datetime
from urllib.parse import urlparse

import requests
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from arc.core import constants
from arc.page_elements import *


def get_message_exception(exception):
    return str(exception).split('\n', 1)[0]


def get_valid_filename(s, max_length=constants.FILENAME_MAX_LENGTH):
    s = str(s).strip().replace(' -- @', '_')
    s = re.sub(r'(?u)[^-\w]', '_', s).strip('_')
    return s[:max_length]


class Utils(object):
    _window_size = None

    def __init__(self, driver_wrapper=None):
        from arc.core.driver.driver_manager import DriverManager
        self.driver_wrapper = driver_wrapper if driver_wrapper else DriverManager.get_default_wrapper()
        self.logger = logging.getLogger(__name__)

    def set_implicitly_wait(self):
        implicitly_wait = self.driver_wrapper.config.get_optional('Driver', 'implicitly_wait')
        if implicitly_wait:
            self.driver_wrapper.driver.implicitly_wait(implicitly_wait)

    def get_explicitly_wait(self):
        return int(self.driver_wrapper.config.get_optional('Driver', 'explicitly_wait', '10'))

    def capture_screenshot(self, name):
        from arc.core.driver.driver_manager import DriverManager
        filename = '{0:0=2d}_{1}'.format(DriverManager.screenshots_number, name)
        filename = '{}.png'.format(get_valid_filename(filename))
        filepath = os.path.join(DriverManager.screenshots_directory, filename)
        if not os.path.exists(DriverManager.screenshots_directory):
            os.makedirs(DriverManager.screenshots_directory)
        if self.driver_wrapper.driver.get_screenshot_as_file(filepath):
            self.logger.info('Screenshot saved in %s', filepath)
            DriverManager.screenshots_number += 1
            return filepath
        return None

    def save_webdriver_logs(self, test_name):
        try:
            log_types = self.driver_wrapper.driver.log_types
        except (Exception,):
            # geckodriver does not implement log_types, but it implements get_log for client and server
            log_types = ['client', 'server']

        self.logger.debug("Reading logs from '%s' and writing them to log files", ', '.join(log_types))
        for log_type in log_types:
            try:
                self.save_webdriver_logs_by_type(log_type, test_name)
            except (Exception,):
                # Capture exceptions to avoid errors in teardown method
                pass

    def save_webdriver_logs_by_type(self, log_type, test_name):
        try:
            logs = self.driver_wrapper.driver.get_log(log_type)
        except (Exception,):
            return

        if len(logs) > 0:
            from arc.core.driver.driver_manager import DriverManager

            log_file_name = '{}_{}.txt'.format(get_valid_filename(test_name), log_type)
            log_file_name = os.path.join(DriverManager.logs_directory, log_file_name)
            with open(log_file_name, 'a+', encoding='utf-8') as log_file:
                driver_type = self.driver_wrapper.config.get('Driver', 'type')
                log_file.write(
                    u"\n{} '{}' test logs with driver = {}\n\n".format(datetime.now(), test_name, driver_type))
                for entry in logs:
                    timestamp = datetime.fromtimestamp(float(entry['timestamp']) / 1000.).strftime(
                        '%Y-%m-%d %H:%M:%S.%f')
                    log_file.write(u'{}\t{}\t{}\n'.format(timestamp, entry['level'], entry['message'].rstrip()))

    def discard_logcat_logs(self):
        if self.driver_wrapper.is_android_test():
            try:
                self.driver_wrapper.driver.get_log('logcat')
            except (Exception,):
                pass

    @staticmethod
    def get_locator_by(by: str):
        by = str(by).lower()
        if by == 'xpath':
            return By.XPATH
        elif by == 'id':
            return By.ID
        elif by == 'link text':
            return By.LINK_TEXT
        elif by == 'name':
            return By.NAME
        elif by == 'tag name':
            return By.TAG_NAME
        elif by == 'class name':
            return By.CLASS_NAME
        elif by == 'css selector':
            return By.CSS_SELECTOR
        elif by == 'partial link text':
            return By.PARTIAL_LINK_TEXT
        else:
            return None

    def _expected_condition_find_element(self, element):
        web_element = False
        try:
            from arc.page_elements import PageElement
            if isinstance(element, PageElement):
                # Use _find_web_element() instead of web_element to avoid logging error message
                element._web_element = None
                element._find_web_element()
                web_element = element._web_element
            elif isinstance(element, tuple):
                web_element = self.driver_wrapper.driver.find_element(*element)
        except NoSuchElementException:
            pass
        return web_element

    def _expected_condition_find_element_visible(self, element):
        web_element = self._expected_condition_find_element(element)
        try:
            return web_element if web_element and web_element.is_displayed() else False
        except StaleElementReferenceException:
            return False

    def _expected_condition_find_element_not_visible(self, element):
        web_element = self._expected_condition_find_element(element)
        try:
            return True if not web_element or not web_element.is_displayed() else False
        except StaleElementReferenceException:
            return False

    def _expected_condition_find_first_element(self, elements):
        from arc.page_elements import PageElement
        element_found = None
        for element in elements:
            try:
                if isinstance(element, PageElement):
                    element._web_element = None
                    element._find_web_element()
                else:
                    self.driver_wrapper.driver.find_element(*element)
                element_found = element
                break
            except (NoSuchElementException, TypeError):
                pass
        return element_found

    def _expected_condition_find_element_clickable(self, element):
        web_element = self._expected_condition_find_element_visible(element)
        try:
            return web_element if web_element and web_element.is_enabled() else False
        except StaleElementReferenceException:
            return False

    def _expected_condition_find_element_stopped(self, element_times):
        element, times = element_times
        web_element = self._expected_condition_find_element(element)
        try:
            locations_list = [tuple(web_element.location.values()) for _ in range(int(times)) if not time.sleep(0.001)]
            return web_element if set(locations_list) == set(locations_list[-1:]) else False
        except StaleElementReferenceException:
            return False

    def _expected_condition_find_element_containing_text(self, element_text_pair):
        element, text = element_text_pair
        web_element = self._expected_condition_find_element(element)
        try:
            return web_element if web_element and text in web_element.text else False
        except StaleElementReferenceException:
            return False

    def _expected_condition_find_element_not_containing_text(self, element_text_pair):
        element, text = element_text_pair
        web_element = self._expected_condition_find_element(element)
        try:
            return web_element if web_element and text not in web_element.text else False
        except StaleElementReferenceException:
            return False

    def _expected_condition_value_in_element_attribute(self, element_attribute_value):
        element, attribute, value = element_attribute_value
        web_element = self._expected_condition_find_element(element)
        try:
            return web_element if web_element and web_element.get_attribute(attribute) == value else False
        except StaleElementReferenceException:
            return False

    def _wait_until(self, condition_method, condition_input, timeout=None):
        # Remove implicitly wait timeout
        self.driver_wrapper.driver.implicitly_wait(0)
        # Get explicitly wait timeout
        timeout = timeout if timeout else self.get_explicitly_wait()
        # Wait for condition
        condition_response = WebDriverWait(self.driver_wrapper.driver, timeout).until(
            lambda s: condition_method(condition_input))
        # Restore implicitly wait timeout from properties
        self.set_implicitly_wait()
        return condition_response

    def wait_until_element_present(self, element, timeout=None):
        return self._wait_until(self._expected_condition_find_element, element, timeout)

    def wait_until_element_visible(self, element, timeout=None):
        return self._wait_until(self._expected_condition_find_element_visible, element, timeout)

    def wait_until_element_not_visible(self, element, timeout=None):
        return self._wait_until(self._expected_condition_find_element_not_visible, element, timeout)

    def wait_until_first_element_is_found(self, elements, timeout=None):
        try:
            return self._wait_until(self._expected_condition_find_first_element, elements, timeout)
        except TimeoutException as exception:
            msg = 'None of the page elements has been found after %s seconds'
            timeout = timeout if timeout else self.get_explicitly_wait()
            self.logger.error(msg, timeout)
            exception.msg += "\n  {}".format(msg % timeout)
            raise exception

    def wait_until_element_clickable(self, element, timeout=None):
        return self._wait_until(self._expected_condition_find_element_clickable, element, timeout)

    def wait_until_element_stops(self, element, times=1000, timeout=None):
        return self._wait_until(self._expected_condition_find_element_stopped, (element, times), timeout)

    def wait_until_element_contains_text(self, element, text, timeout=None):
        return self._wait_until(self._expected_condition_find_element_containing_text, (element, text), timeout)

    def wait_until_element_not_contain_text(self, element, text, timeout=None):
        return self._wait_until(self._expected_condition_find_element_not_containing_text, (element, text), timeout)

    def wait_until_element_attribute_is(self, element, attribute, value, timeout=None):
        return self._wait_until(self._expected_condition_value_in_element_attribute, (element, attribute, value),
                                timeout)

    def wait_presence_of_element_located(self, driver, by, locator, delay=30):
        loc_by = self.get_locator_by(by)
        element = WebDriverWait(driver, delay).until(ec.presence_of_element_located((loc_by, locator)))
        return element

    def wait_frame_to_be_available_and_switch_to_it(self, driver, by, locator, delay=30):
        loc_by = self.get_locator_by(by)
        element = WebDriverWait(driver, delay).until(ec.frame_to_be_available_and_switch_to_it((loc_by, locator)))
        return element

    def get_remote_node(self):
        logging.getLogger("requests").setLevel(logging.WARNING)
        remote_node = None
        server_type = 'local'
        if self.driver_wrapper.config.getboolean_optional('Server', 'enabled'):
            # Request session info from grid hub
            session_id = self.driver_wrapper.driver.session_id
            self.logger.debug("Trying to identify remote node")
            try:
                # Request session info from grid hub and extract remote node
                url = '{}/grid/api/testsession?session={}'.format(self.get_server_url(),
                                                                  session_id)
                proxy_id = requests.get(url).json()['proxyId']
                remote_node = urlparse(proxy_id).hostname if urlparse(proxy_id).hostname else proxy_id
                server_type = 'grid'
                self.logger.debug("Test running in remote node %s", remote_node)
            except (ValueError, KeyError):
                try:
                    # Request session info from GGR and extract remote node

                    from arc.integrations.selenoid import Selenoid
                    remote_node = Selenoid(self.driver_wrapper).get_selenoid_info()['Name']
                    server_type = 'ggr'
                    self.logger.debug("Test running in a GGR remote node %s", remote_node)
                except (Exception,):
                    try:
                        # The remote node is a Selenoid node
                        url = '{}/status'.format(self.get_server_url())
                        total = requests.get(url).json()['total']
                        remote_node = self.driver_wrapper.config.get('Server', 'host')
                        server_type = 'selenoid'
                        self.logger.debug(f"Test running in a Selenoid node {remote_node}")
                        self.logger.debug(f"Test running total in Selenoid node {total}")
                    except (Exception,):
                        # The remote node is not a grid node or the session has been closed
                        remote_node = self.driver_wrapper.config.get('Server', 'host')
                        server_type = 'selenium'
                        self.logger.debug("Test running in a Selenium node %s", remote_node)

        return server_type, remote_node

    def get_server_url(self):
        server_host = self.driver_wrapper.config.get('Server', 'host')
        server_port = self.driver_wrapper.config.get('Server', 'port')
        server_username = self.driver_wrapper.config.get_optional('Server', 'username')
        server_password = self.driver_wrapper.config.get_optional('Server', 'password')
        server_auth = '{}:{}@'.format(server_username, server_password) if server_username and server_password else ''
        server_url = 'https://{}{}:{}'.format(server_auth, server_host, server_port)
        return server_url

    def download_remote_video(self, remote_node, session_id, video_name):
        try:
            video_url = self._get_remote_video_url(remote_node, session_id)
        except requests.exceptions.ConnectionError:
            self.logger.warning("Remote server seems not to have video capabilities")
            return

        if not video_url:
            self.logger.warning("Test video not found in node '%s'", remote_node)
            return

        self._download_video(video_url, video_name)

    @staticmethod
    def _get_remote_node_url(remote_node):
        logging.getLogger("requests").setLevel(logging.WARNING)
        grid_extras_port = 3000
        return 'http://{}:{}'.format(remote_node, grid_extras_port)

    def _get_remote_video_url(self, remote_node, session_id):
        url = '{}/video'.format(self._get_remote_node_url(remote_node))
        timeout = time.time() + 5  # 5 seconds from now

        # Requests videos list until timeout or the video url is found
        video_url = None
        while time.time() < timeout:
            response = requests.get(url).json()
            try:
                video_url = response['available_videos'][session_id]['download_url']
                break
            except KeyError:
                time.sleep(1)
        return video_url

    def _download_video(self, video_url, video_name):
        from arc.core.driver.driver_manager import DriverManager
        filename = '{0:0=2d}_{1}'.format(DriverManager.videos_number, video_name)
        filename = '{}.mp4'.format(get_valid_filename(filename))
        filepath = os.path.join(DriverManager.videos_directory, filename)
        if not os.path.exists(DriverManager.videos_directory):
            os.makedirs(DriverManager.videos_directory)
        response = requests.get(video_url)
        open(filepath, 'wb').write(response.content)
        self.logger.info("Video saved in '%s'", filepath)
        DriverManager.videos_number += 1

    def is_remote_video_enabled(self, remote_node):
        enabled = False
        if remote_node:
            url = '{}/config'.format(self._get_remote_node_url(remote_node))
            try:
                response = requests.get(url, timeout=5).json()
                record_videos = response['config_runtime']['theConfigMap']['video_recording_options'][
                    'record_test_videos']
            except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout, KeyError):
                record_videos = 'false'
            if record_videos == 'true':
                # Wait to the video recorder start
                time.sleep(1)
                enabled = True
        return enabled

    def get_center(self, element):
        web_element = self.get_web_element(element)
        location = web_element.location
        size = web_element.size
        return {'x': location['x'] + (size['width'] / 2), 'y': location['y'] + (size['height'] / 2)}

    def get_safari_navigation_bar_height(self):
        status_bar_height = 0
        if self.driver_wrapper.is_ios_test() and self.driver_wrapper.is_web_test():
            # ios 7.1, 8.3
            status_bar_height = 64
        return status_bar_height

    def get_window_size(self):
        if not self._window_size:
            if self.driver_wrapper.is_android_web_test() and self.driver_wrapper.driver.current_context != 'NATIVE_APP':
                window_width = self.driver_wrapper.driver.execute_script("return window.innerWidth")
                window_height = self.driver_wrapper.driver.execute_script("return window.innerHeight")
                self._window_size = {'width': window_width, 'height': window_height}
            else:
                self._window_size = self.driver_wrapper.driver.get_window_size()
        return self._window_size

    def get_native_coords(self, coords):
        web_window_size = self.get_window_size()
        self.driver_wrapper.driver.switch_to.context('NATIVE_APP')
        native_window_size = self.driver_wrapper.driver.get_window_size()
        scale = native_window_size['width'] / web_window_size['width']
        offset_y = self.get_safari_navigation_bar_height()
        native_coords = {'x': coords['x'] * scale, 'y': coords['y'] * scale + offset_y}
        self.logger.debug('Converted web coords %s into native coords %s', coords, native_coords)
        return native_coords

    def swipe(self, element, x, y, duration=None):
        if not self.driver_wrapper.is_mobile_test():
            raise Exception('Swipe method is not implemented in Selenium')

        # Get center coordinates of element
        center = self.get_center(element)
        initial_context = self.driver_wrapper.driver.current_context
        if self.driver_wrapper.is_web_test() or initial_context != 'NATIVE_APP':
            center = self.get_native_coords(center)

        # Android needs absolute end coordinates and ios needs movement
        end_x = x if self.driver_wrapper.is_ios_test() else center['x'] + x
        end_y = y if self.driver_wrapper.is_ios_test() else center['y'] + y
        self.driver_wrapper.driver.swipe(center['x'], center['y'], end_x, end_y, duration)

        if self.driver_wrapper.is_web_test() or initial_context != 'NATIVE_APP':
            self.driver_wrapper.driver.switch_to.context(initial_context)

    def get_web_element(self, element):
        from arc.page_elements import PageElement
        if isinstance(element, WebElement):
            web_element = element
        elif isinstance(element, PageElement):
            web_element = element.web_element
        elif isinstance(element, tuple):
            web_element = self.driver_wrapper.driver.find_element(*element)
        else:
            web_element = None
        return web_element

    def get_first_webview_context(self):
        for context in self.driver_wrapper.driver.contexts:
            if context.startswith('WEBVIEW'):
                return context
        raise Exception('No WEBVIEW context has been found')

    def switch_to_first_webview_context(self):
        self.driver_wrapper.driver.switch_to.context(self.get_first_webview_context())

    def highlight_element(self, context, element, color, border):
        is_page_element = self.is_page_element_instance(element)
        if is_page_element is True:
            element = self.convert_to_selenium_element(context, element)

        original_style = element.get_attribute('style')
        style = "border: {0}px solid {1};".format(border, color)
        context.driver.execute_script("arguments[0].setAttribute('style', arguments[1]);", element, style)
        return original_style

    @staticmethod
    def is_page_element_instance(element):
        page_element_instances = (Button, Text, InputText, InputRadio, Link, Checkbox, Select, Group)
        is_page_element = False
        if isinstance(element, page_element_instances):
            is_page_element = True

        return is_page_element

    @staticmethod
    def convert_to_selenium_element(context, page_element):
        by, loc = page_element.locator
        if by == 'xpath':
            page_element = context.driver.find_element(By.XPATH, loc)
        elif by == 'id':
            page_element = context.driver.find_element(By.ID, loc)
        elif by == 'link text':
            page_element = context.driver.find_element(By.LINK_TEXT, loc)
        elif by == 'name':
            page_element = context.driver.find_element(By.NAME, loc)
        elif by == 'tag name':
            page_element = context.driver.find_element(By.TAG_NAME, loc)
        elif by == 'class name':
            page_element = context.driver.find_element(By.CLASS_NAME, loc)
        elif by == 'css selector':
            page_element = context.driver.find_element(By.CSS_SELECTOR, loc)
        elif by == 'partial link text':
            page_element = context.driver.find_element(By.PARTIAL_LINK_TEXT, loc)
        return page_element
