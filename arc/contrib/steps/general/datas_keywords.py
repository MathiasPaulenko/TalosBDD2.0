from behave import use_step_matcher, step

from arc.contrib.tools import files

use_step_matcher("re")


#######################################################################################################################
#                                                  Files Steps                                                        #
#######################################################################################################################
@step(u"add to the json file with path '(?P<file_path>.+)' the key '(?P<key>.+)' with the value '(?P<value>.+)'")
def add(context, file_path, key, value):
    files.set_value_json_path(file_path, key, value)


@step(u"delete to the json file with path '(?P<file_path>.+)' the value with key '(?P<key>.+)'")
def add(context, file_path, key):
    files.delete_value_json_path(file_path, key)


@step(u"add to the yaml file with path '(?P<file_path>.+)' the key '(?P<key>.+)' with the value '(?P<value>.+)'")
def add(context, file_path, key, value):
    files.set_value_yaml_path(file_path, key, value)


@step(u"delete to the yaml file with path '(?P<file_path>.+)' the value with key '(?P<key>.+)'")
def add(context, file_path, key):
    files.delete_value_yaml_path(file_path, key)


#######################################################################################################################
#                                                  Context Steps                                                      #
#######################################################################################################################
@step(u"add to the context a data dictionary of the yaml file with path '(?P<file_path>.+)'")
def add(context, file_path):
    context.runtime.dict_yaml = files.yaml_to_dict(file_path)


@step(u"add to the context a data dictionary of the json file with path '(?P<file_path>.+)'")
def add(context, file_path):
    context.runtime.dict_json = files.json_to_dict(file_path)


@step(u"add to the context the value of a key path '(?P<key_path>.+)' of the json file with path '(?P<file_path>.+)'")
def add(context, key_path, file_path):
    context.runtime.json_key_path_value = files.get_json_value_key_path(key_path, file_path, sep_char=".")


@step(u"add to the profiles files '(?P<file_name>.+)' the key '(?P<key>.+)' with the value '(?P<value>.+)'")
def add(context, file_name, key, value):
    files.set_profile_data_value(file_name, key, value, change_all_profiles=False)


@step(u"add to the profiles files '(?P<file_name>.+)' the key '(?P<key>.+)' with the value '(?P<value>.+)' with spread")
def add(context, file_name, key, value):
    files.set_profile_data_value(file_name, key, value, change_all_profiles=True)


@step(u"delete to the profiles files '(?P<file_name>.+)' the value with the key '(?P<key>.+)'")
def add(context, file_name, key):
    files.delete_profile_data_value(file_name, key, change_all_profiles=False)


@step(u"delete to the profiles files '(?P<file_name>.+)' the value with the key '(?P<key>.+)' with spread")
def add(context, file_name, key):
    files.delete_profile_data_value(file_name, key, change_all_profiles=True)
