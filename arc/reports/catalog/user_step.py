import importlib
import os
from importlib import util

from arc.reports.catalog.pydoc_formatter import get_pydoc_info

STEPS_PATH = os.path.abspath(os.path.join(os.path.abspath(__file__), os.pardir) + '/../../../steps')


def get_user_step_imports():
    imports = []
    for root, dirs, files in os.walk(STEPS_PATH):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                spec = importlib.util.spec_from_file_location("*", file_path)
                modules = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(modules)
                imports.append(modules)
    return imports


def get_list_user_steps():
    imports = get_user_step_imports()
    data_list = []
    for imp in imports:
        data_list.append(get_pydoc_info(imp))

    return data_list
