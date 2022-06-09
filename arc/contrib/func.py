# TODO: posible refactorización
# mover a una fichero de evidenciación y separar funciones por tipo
import json
import re
from copy import deepcopy

from arc.contrib.utilities import Utils


class Func:
    context: None

    def __init__(self, context):
        self.context = context

    def add_extra_info(self, capture_name=None, text=None):
        exec_type = self.context.pytalos_config.get('Driver', 'type')
        if capture_name is not None and text is not None:
            self.context.extra_info_dict.append(text)
            if exec_type != "api":
                utils = Utils()
                path = utils.capture_screenshot(str(capture_name))
                self.context.extra_info_dict.append(path)

        elif capture_name is not None:
            if exec_type != "api":
                utils = Utils()
                path = utils.capture_screenshot(str(capture_name))
                self.context.extra_info_dict.append(path)

        elif text is not None:
            self.context.extra_info_dict.append(text)

        elif capture_name is None and text is None:
            raise Exception("capture_name or text must be filled in")

    def add_formatter_evidence_json(self, json_origin: dict, title):
        try:
            json_evidence = deepcopy(json_origin)
            json_evidence["TITLE_EVIDENCE"] = title
            self.context.api_evidence_manual_extra_json.append(json_evidence)
        except Exception as ex:
            print(ex)

    def get_profile_value_key_path(self, param_path_key, file_name, sep_char: str = "."):
        params_list = param_path_key.split(sep_char)
        profiles_datas = self.context.config.userdata
        dict_json = profiles_datas[file_name]
        aux_json = deepcopy(dict_json)
        for param in params_list:
            if type(aux_json) is list:
                aux_json = aux_json[int(param)]
            else:
                aux_json = aux_json[param]
        return aux_json

    def get_unique_profile_re_var(self, initial_value, file_name):
        if re.match(r"{{(.*?)\}\}", initial_value):
            value = str(initial_value).replace("{{", "").replace("}}", "")
        else:
            value = initial_value

        return self.get_profile_value_key_path(value, file_name)

    @staticmethod
    def is_contains_profile_re_var(initial_value):
        if "{{" and "}}" in str(initial_value):
            return True
        else:
            return False

    def get_formatter_multiple_re_var(self, text, file_name):
        matchers = re.findall(r"{{(.*?)\}\}", text)

        for match in matchers:
            text = str(text).replace("{{" + match + "}}", str(self.get_profile_value_key_path(match, file_name)))

        return text

    def get_template_var_value(self, template_var, profile_file='master'):
        if profile_file == 'master':
            data_file = self.context.master_file_name_config
        else:
            data_file = profile_file

        if self.is_contains_profile_re_var(template_var):
            return self.get_unique_profile_re_var(template_var, data_file)
        else:
            return template_var

    @staticmethod
    def format_evidence_json(data):
        return json.dumps(data, sort_keys=True, indent=4)

    def generate_table_evidence(self, name, key=None, value_expected=None, current_value=None, result_flag=None,
                                error_message=None, schema_type=None):
        dictionary = {"Verify_Name": name}
        if key:
            dictionary["Key"] = str(key)
        if current_value:
            dictionary["Current Value"] = current_value
        if value_expected:
            dictionary["Expected Value"] = value_expected
        if schema_type:
            dictionary["Input Schema Type"] = schema_type

        if result_flag == 'True':
            result_flag = 'Passed'
        elif result_flag == 'False':
            result_flag = 'Failed'

        dictionary["Assert Result"] = result_flag
        dictionary["Error Message"] = error_message
        self.context.api_evidence_verify.append(dictionary)
