# -*- coding: utf-8 -*-

import os
import time

import requests
from arc.core import constants


class Selenoid(object):

    def __init__(self, driver_wrapper, **kwargs):
        self.driver_wrapper = driver_wrapper
        from arc.core.driver.driver_manager import DriverManager
        self.videos_directory = kwargs.get('videos_dir', DriverManager.videos_directory)
        self.logs_directory = kwargs.get('logs_dir', DriverManager.logs_directory)
        self.output_directory = kwargs.get('output_dir', DriverManager.output_directory)
        self.browser_remote = driver_wrapper.config.getboolean_optional('Server', 'enabled', False)
        self.browser = driver_wrapper.driver.desired_capabilities['browserName']

        if self.browser_remote:
            self.session_id = driver_wrapper.driver.session_id
            self.server_url = driver_wrapper.utils.get_server_url()

    def __download_file(self, url, path_file, timeout):
        status_code = 0
        init_time = time.time()
        self.driver_wrapper.logger.info(f"Downloading file from Selenoid node: {url}")

        body = None
        while status_code != constants.SEL_STATUS_OK and time.time() - init_time < float(timeout):
            body = requests.get(url)
            status_code = body.status_code
            if status_code != constants.SEL_STATUS_OK:
                time.sleep(1)
        took = time.time() - init_time
        if status_code == constants.SEL_STATUS_OK:
            path, name = os.path.split(path_file)
            if not os.path.exists(path):
                os.makedirs(path)
            try:
                fp = open(path_file, 'wb')
                fp.write(body.content)
                fp.close()
                self.driver_wrapper.logger.info(
                    f"File has been downloaded successfully to {path_file} and took {took} seconds")
                return True
            except IOError as e:
                self.driver_wrapper.logger.warn(f"Error writing downloaded file in {path_file}:\n {e}")
        else:
            self.driver_wrapper.logger.warn(f"File {url} does not exist in the server after {timeout} seconds")
        return False

    @staticmethod
    def __remove_file(url):
        requests.delete(url)

    def get_selenoid_info(self):
        host_url = f"{self.server_url}/host/{self.session_id}"
        try:
            selenoid_info = requests.get(host_url).json()
        except Exception as ex:
            self.driver_wrapper.logger.warn(ex)
            return None

        self.driver_wrapper.logger.info(f"Selenoid host info: \n {selenoid_info}")
        return selenoid_info

    def is_the_session_still_active(self):
        server_url_list = self.server_url.split(":")
        host_url = f"{server_url_list[0]}:{server_url_list[1]}:{server_url_list[2]}:{constants.SEL_STATUS_PORT}/status"
        response = None
        try:
            response = requests.get(host_url).json()["browsers"][self.browser]
        except Exception as e:
            self.driver_wrapper.logger.warn(
                f"the GGR status request has failed: \nResponse: {response.content} \nError message: {e}\n")
            return None
        for browser in response:
            if response[browser] != {}:
                sessions = response[browser][server_url_list[1].split("@")[0].replace("//", "")]["sessions"]
                for session in sessions:
                    if session["id"] == self.session_id:
                        return True
        return False

    def download_session_video(self, scenario_name, timeout=5):
        if (self.driver_wrapper.get_driver_platform().lower() != 'linux' or
                not self.driver_wrapper.config.getboolean_optional('Capabilities', 'enableVideo')):
            return

        path_file = os.path.join(self.videos_directory, '%s.%s' % (scenario_name, constants.SEL_MP4_EXTENSION))
        if self.driver_wrapper.server_type == 'selenoid':
            filename = '%s.%s' % (self.session_id, constants.SEL_MP4_EXTENSION)
        else:
            filename = self.session_id

        video_url = f"{self.server_url}/video/{filename}"
        if self.browser_remote:
            self.__download_file(video_url, path_file, timeout)
        self.__remove_file(video_url)

    def download_session_log(self, scenario_name, timeout=5):
        if (self.driver_wrapper.get_driver_platform().lower() != 'linux' or
                not self.driver_wrapper.config.getboolean_optional('Capabilities', 'enableLog')):
            return

        path_file = os.path.join(self.logs_directory, '%s_ggr.%s' % (scenario_name, constants.SEL_LOG_EXTENSION))
        if self.driver_wrapper.server_type == 'selenoid':
            filename = '%s.%s' % (self.session_id, constants.SEL_LOG_EXTENSION)
        else:
            filename = self.session_id

        logs_url = f"{self.server_url}/logs/{filename}"

        if self.browser_remote:
            self.__download_file(logs_url, path_file, timeout)
        self.__remove_file(logs_url)

    def download_file(self, filename, timeout=5):
        path_file = os.path.join(self.output_directory, constants.SEL_DOWNLOADS_PATH, self.session_id[-8:], filename)
        file_url = f"{self.server_url}/download/{self.session_id}/{filename}"

        if self.browser_remote:
            self.__download_file(file_url, path_file, timeout)
            return path_file
        return None
