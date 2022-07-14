import os
import shutil
from settings import settings
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import IEDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from arc.core import constants


def _disabled_proxy():
    if settings.PYTALOS_GENERAL['update_driver']['enable_proxy']:
        os.environ["HTTP_PROXY"] = ""
        os.environ["HTTPS_PROXY"] = ""


def _enabled_proxy():
    if settings.PYTALOS_GENERAL['update_driver']['enable_proxy']:
        os.environ["HTTP_PROXY"] = settings.PYTALOS_GENERAL['update_driver']['proxy']['http_proxy']
        os.environ["HTTPS_PROXY"] = settings.PYTALOS_GENERAL['update_driver']['proxy']['https_proxy']


class InstallDriver:
    temp_path = 'settings/temp_drivers'
    drivers_path = 'settings/drivers/'

    def __init__(self, driver_name):
        self.driver_name = driver_name

    def _create_temp_folder(self):
        if not os.path.exists(self.temp_path):
            os.mkdir(self.temp_path)

    def _delete_temp_folder(self):
        if os.path.exists(self.temp_path):
            shutil.rmtree(self.temp_path)

    def _move_driver(self, driver_path):
        shutil.move(driver_path, self.drivers_path + self.driver_name)

    def _download_driver(self, driver):
        if driver == constants.IEXPLORE:
            driver_path = IEDriverManager(path=self.temp_path).install()
        elif driver == constants.CHROME:
            driver_path = ChromeDriverManager(path=self.temp_path).install()
        elif driver == constants.EDGE:
            driver_path = EdgeChromiumDriverManager(path=self.temp_path).install()
        elif driver == constants.FIREFOX:
            driver_path = GeckoDriverManager(path=self.temp_path).install()
        return driver_path

    def install_driver(self, driver):
        _enabled_proxy()
        self._create_temp_folder()
        driver_path = self._download_driver(driver)
        self._move_driver(driver_path)
        self._delete_temp_folder()
        _disabled_proxy()
