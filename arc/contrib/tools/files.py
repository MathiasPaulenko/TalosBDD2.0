import json
import os
from copy import deepcopy

import yaml

from settings import settings


def is_file_exist(file_path):
    return os.path.isfile(file_path)


def yaml_to_dict(file_path):
    yaml_file = open(file_path, encoding='utf8')
    return yaml.load(yaml_file, Loader=yaml.FullLoader)


def json_to_dict(file_path):
    with open(file_path, encoding='utf8') as file:
        return json.load(file)


def get_json_value_key_path(param_path_key, file_path, sep_char: str = "."):
    params_list = param_path_key.split(sep_char)
    dict_json = json_to_dict(file_path)
    aux_json = deepcopy(dict_json)

    for param in params_list:
        if type(aux_json) is list:
            aux_json = aux_json[int(param)]
        else:
            aux_json = aux_json[param]
    return aux_json


def set_value_json_path(file_path, key, value):
    with open(file_path, encoding='utf8') as json_file:
        json_decoded = json.load(json_file)

    json_decoded[key] = value

    with open(file_path, 'w', encoding='utf8') as json_file:
        json.dump(json_decoded, json_file)


def delete_value_json_path(file_path, key):
    with open(file_path, encoding='utf8') as json_file:
        json_decoded = json.load(json_file)

    del json_decoded[key]

    with open(file_path, 'w', encoding='utf8') as json_file:
        json.dump(json_decoded, json_file)


def set_value_yaml_path(file_path, key, values):
    with open(file_path, encoding='utf8') as f:
        doc = yaml.load(f)

    doc[key] = values

    with open(file_path, 'w', encoding='utf8') as f:
        yaml.dump(doc, f)


def delete_value_yaml_path(file_path, key):
    with open(file_path, encoding='utf8') as f:
        doc = yaml.load(f)

    del doc[key]

    with open(file_path, 'w', encoding='utf8') as f:
        yaml.dump(doc, f)


def set_profile_data_value(file_name, key, value, change_all_profiles=True):
    directory_list = []
    file_names = []

    for root, dirs, files in os.walk("settings/profiles", topdown=False):
        for file in files:
            if file not in file_names:
                file_names.append(file)
        for name in dirs:
            directory_list.append(name)
    if change_all_profiles:
        for directory in directory_list:
            for file in file_names:
                if file.split(".")[0] == file_name:
                    try:
                        path = "settings/profiles/" + directory + "/" + file
                        if file.split(".")[1] == "json":
                            set_value_json_path(path, key, value)
                        elif file.split(".")[1] == "yaml":
                            set_value_yaml_path(path, key, value)
                    except FileNotFoundError:
                        pass
    else:
        for file in file_names:
            if file.split(".")[0] == file_name:
                try:
                    path = "settings/profiles/" + settings.PYTALOS_PROFILES['environment'] + "/" + file
                    if file.split(".")[1] == "json":
                        set_value_json_path(path, key, value)
                    elif file.split(".")[1] == "yaml":
                        set_value_yaml_path(path, key, value)
                except FileNotFoundError:
                    pass


def delete_profile_data_value(file_name, key, change_all_profiles=True):
    directory_list = []
    file_names = []

    for root, dirs, files in os.walk("settings/profiles", topdown=False):
        for file in files:
            if file not in file_names:
                file_names.append(file)
        for name in dirs:
            directory_list.append(name)
    if change_all_profiles:
        for directory in directory_list:
            for file in file_names:
                if file.split(".")[0] == file_name:
                    try:
                        path = "settings/profiles/" + directory + "/" + file
                        if file.split(".")[1] == "json":
                            delete_value_json_path(path, key)
                        elif file.split(".")[1] == "yaml":
                            delete_value_yaml_path(path, key)
                    except FileNotFoundError:
                        pass
    else:
        for file in file_names:
            if file.split(".")[0] == file_name:
                try:
                    path = "settings/profiles/" + settings.PYTALOS_PROFILES['environment'] + "/" + file
                    if file.split(".")[1] == "json":
                        delete_value_json_path(path, key)
                    elif file.split(".")[1] == "yaml":
                        delete_value_yaml_path(path, key)
                except FileNotFoundError:
                    pass
