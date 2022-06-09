import os

from arc.settings import settings

DRIVERS_HOME = settings.DRIVERS_HOME


def add_drivers_directory_to_path(path=DRIVERS_HOME):
    os.environ["PATH"] = path + ';' + os.environ["PATH"]
