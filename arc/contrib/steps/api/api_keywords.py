"""
API Default Keywords
Default steps for use in Gherkin features.
In each step there is the documentation of what it is for and how to use it, as well as an example.
In some steps, not only is the desired operation performed, but it also adds extra information to the Word evidence.

List of steps:
######################################################################################################################

## Request Steps:
send request
clear last request datas

## Prepare Request Steps
prepare the headers request with file path {file_path}
prepare the headers request with key path {key_path} in file {file_name}
prepare data headers request with file name
prepare the headers request
prepare the body request with file path {file_path}
prepare the body request with key path {key_path} in file {file_name}
prepare the body request
prepare data body request with file name
prepare the method {method} request
prepare the uri request with key path {key_path} in file {file_name}
prepare uri with key {key_path} in file {file_name} with resource {uri_path}
prepare the uri {uri} request
prepare the uri {uri} request with path {path}
prepare the params request with file path {file_path}
prepare the params request with key path {key_path} in file {file_name}
prepare the params request
prepare data params request with file name
set ssl verify value {ssl}
prepare cookies from the previous request
prepare the data payload request with file path {file_path}
prepare the data payload request with key path {key_path} in file {file_name}
prepare the data payload request
prepare the multiple files request
prepare the files request

## Verifications Steps
verify simple value {value} of type {value_type} in key {key}
verify value {value} of type {value_type} in path key {key}
validate the response scheme with the json file in the path {file_path}
validate the response scheme with the key path {key_path} in file {file_name}
validate the response scheme with the key path {key_path} in file path {file_path}
validate response schema with key path and file name in table
validate response schema with key path and file path
validate schema: key {key_path}, file name {file_name}
verify response contains value {value} of type {value_type}
verify response contains value {value}
verify response headers contains value {value} of type {value_type}
verify status reason is {reason}
verify the value of the key {key} is of type {value_type}
verify status code is {status_code}
verify type value {value_type} in path key {key}
verify response headers contains {headers}
verify response contains key {key}
verify status code is one of {status_code}
verify response time is between {less_expected} and {greater_expected}
verify response time is less than {second_expected}
verify response time is greater than {second_expected}

## Authorization Steps
create basic authorization
create basic authorization with username {username} and password {password}
create digest authorization
create digest authorization with username {username} and password {password}
create oauth1 authorization
create oauth2 authorization
create mobile oauth2 authorization with client id {cid}, url {url} and scope {scope}
create legacy oauth2 authorization with client id {client_id}
create backend oauth2 authorization with client id {client_id}

## Response Steps
save response encoding
create response image binary
save response in the file with path {file_path}
add to the profile file {file_name} the response key value {r_key} with key {key}

## Proxies Steps
configure the proxies with file path {file_path}
configure the proxies with key path {key_path} in file {file_name}
configure the proxies request
######################################################################################################################
"""
import operator
from array import array
from functools import reduce

from behave import use_step_matcher, step

from arc.contrib.tools import files

use_step_matcher("re")


#######################################################################################################################
#                                                  Request Steps                                                      #
#######################################################################################################################
@step(u"send request")
def send_request(context):
    """
    This step launches the request with the data prepared in the previous preparation steps.
    Save the response in the context variable= context.response
    :example
        When send request
    :
    :tag API Request step:
    :param context:
    :return context.response:
    """
    context.response = context.api.send_request()


@step(u"clear last request datas")
def clear_last_request_datas(context):
    """
    This step resets the context.api instance to default.
    WARNING=All the information and objects used and saved in the context.api instance from the previous execution
    will be deleted.
    It is recommended to use this step only if you are going to make two calls on the same SCENARIO
    And only if the objective of the first call is to store a value in a profile file or within the context.
    If not, it is recommended to make one call in the background and the other within the scenario.
    :example
        Then clear last request datas
    :
    :tag API Request step:
    :param context:
    :return:
    """
    from arc.contrib.api import api_wrapper
    context.api_wrapper = api_wrapper
    context.api = context.api_wrapper.ApiObject(context)


#######################################################################################################################
#                                                  Prepare Request Steps                                              #
#######################################################################################################################
@step(u"prepare the headers request with file path '(?P<file_path>.+)'")
def prepare_headers_file_path(context, file_path):
    """
    This step prepares the request headers using a file.
    You have to pass it the path of the file that contains the values of the headers as a json / dictionary.
    The data dictionary of the json file passed by parameter will be saved in the context
    variable context.test_request_headers
    The file_path parameter allows relative paths
    You can also use values with {{variable}} to reference a json / yaml key from the master file
    :example
        When prepare the headers request with file path 'input/profiles/cer/headers.json'

        When prepare the headers request with file path '{{headers}}'

    :
    :tag API Prepare Request Steps:
    :param context:
    :param file_path:
    :return context.test_request_headers:
    """

    if context.func.is_contains_profile_re_var(file_path):
        file_path = context.func.get_formatter_multiple_re_var(file_path, context.master_file_name_config)

    dict_headers = dict(files.json_to_dict(file_path))
    context.api.prepare_request(header=dict_headers)
    context.func.add_formatter_evidence_json(dict_headers, "Prepared headers")
    context.test_request_headers = dict_headers


@step(u"prepare the headers request with key path '(?P<key_path>.+)' in file '(?P<file_name>.+)'")
def prepare_headers_file_path_and_key_path(context, key_path, file_name):
    """
    This step prepares the request headers using a file and key path.
    You have to pass it the name of the profile file that contains the values of the headers as a json / dictionary and
    and the path of keys to the values of the headers:
    Where the separator character for the key paths will be the period "."
    Returning a dictionary with the values with the headers of the json file
    The data dictionary of the json file passed by parameter will be saved in the context
    variable context.test_request_headers
    :example
        When prepare the headers request with key path 'api_name.api_example.headers' in file 'api_datas'
    :
    :tag API Prepare Request Steps:
    :param context:
    :param key_path:
    :param file_name:
    :return context.test_request_headers:
    """
    dict_headers = context.api.get_profile_value_key_path(key_path, file_name)
    context.api.prepare_request(header=dict_headers)
    context.func.add_formatter_evidence_json(dict_headers, "Prepared headers")
    context.test_request_headers = dict_headers


@step(u"prepare data headers request with file name")
def prepare_headers_with_file_name(context):
    """
    This step prepares the request headers using data table of Gherkin added another column with profile file name.
    The data dictionary of the json file passed by parameter will be saved in the
    context variable context.test_request_headers
    The data table supports third columns, key, value and file_name
    You can also use values with {{variable}} to reference a json / yaml key from the profiles datas

    :example
       When prepare data headers request with file name
          | key      | value      |file_name       |
          | headers1 | valor1     |                |
          | headers2 | {{valor2}} | name           |


        And prepare data headers request with file name
          | key           | value             | file_name       |
          | Authorization | {{Token_JWT}}     | calendars_datas |
          | Content-Type  | application/json  |                 |
          | client_id     | {{Client_ID}}     | calendars_datas |
          | client_secret | {{Client_Secret}} | calendars_datas |
    :
    :tag API Prepare Request Steps:
    :param context:
    :return context.test_request_headers:
    """
    dict_headers = {}
    if context.table:
        for row in context.table:
            if row["file_name"] and context.func.is_contains_profile_re_var(row["value"]):
                value = context.func.get_formatter_multiple_re_var(row["value"], row["file_name"])
            else:
                value = row["value"]

            dict_headers[row["key"]] = value
    context.api.prepare_request(header=dict_headers)
    context.func.add_formatter_evidence_json(dict_headers, "Prepared headers")
    context.test_request_headers = dict_headers


@step(u"prepare the headers request")
def prepare_headers_data_table(context):
    """
    This step prepares the request headers using data table of Gherkin added another column with profile file name.
    The data dictionary of the json file passed by parameter will be saved in the
    context variable context.test_request_headers
    The data table supports third columns, key, value and file_name
    You can also use values with {{variable}} to reference a json / yaml key from the profiles datas

    :example
       When prepare the headers request
          | key      | value      |
          | headers1 | valor1     |
          | headers2 | {{valor2}} |


        And prepare the headers request
          | key           | value             |
          | Authorization | {{Token_JWT}}     |
          | Content-Type  | application/json  |
          | client_id     | {{Client_ID}}     |
          | client_secret | {{Client_Secret}} |
    :
    :tag API Prepare Request Steps:
    :param context:
    :return context.test_request_headers:
    """
    dict_headers = {}
    if context.table:
        for row in context.table:
            if context.func.is_contains_profile_re_var(row["value"]):
                value = context.func.get_formatter_multiple_re_var(row["value"], context.master_file_name_config)
            else:
                value = row["value"]

            dict_headers[row["key"]] = value
    context.api.prepare_request(header=dict_headers)
    context.func.add_formatter_evidence_json(dict_headers, "Prepared headers")
    context.test_request_headers = dict_headers


@step(u"prepare the body request with file path '(?P<file_path>.+)'")
def prepare_body_with_file_path(context, file_path):
    """
    This step prepares the request body using a file.
    You have to pass it the path of the file that contains the values of the body as a json / dictionary.
    The data dictionary of the json file passed by parameter will be saved in the context
    variable context.test_request_body
    The file_path parameter allows relative paths
    You can also use values with {{variable}} to reference a json / yaml key from the master file

    :example
        Given prepare the body request with file path 'input/profiles/cer/body.json'

        Given prepare the body request with file path '{{body_json_path}}'
    :
    :tag API Prepare Request Steps:
    :param context:
    :param file_path:
    :return context.test_request_body:
    """
    if context.func.is_contains_profile_re_var(file_path):
        file_path = context.func.get_formatter_multiple_re_var(file_path, context.master_file_name_config)

    dict_body = dict(files.json_to_dict(file_path))
    context.api.prepare_request(body=dict_body)
    context.func.add_formatter_evidence_json(dict_body, "Prepared body")
    context.test_request_body = dict_body


@step(u"prepare the body request with key path '(?P<key_path>.+)' in file '(?P<file_name>.+)'")
def prepare_body_with_path_key_and_file_name(context, key_path, file_name):
    """
    This step prepares the request body using a profile file name and key path.
    You have to pass it the path of the file that contains the values of the body as a json / dictionary and
    and the path of keys to the values of the body:
    Where the separator character for the key paths will be the period "."
    Returning a dictionary with the values with the body of the json file
    The data dictionary of the json file passed by parameter will be saved in the context
    variable context.test_request_body
    You can also use values with {{variable}} to reference a json / yaml key from the profile file name
    :example
        When prepare the body request with key path 'api_name.api_example.body' in file 'api_datas'

        When prepare the body request with key path '{{key_path_body}}' in file 'api_datas'

    :
    :tag API Prepare Request Steps:
    :param context:
    :param key_path:
    :param file_name:
    :return context.test_request_body:
    """
    if context.func.is_contains_profile_re_var(key_path):
        key_path = context.func.get_formatter_multiple_re_var(key_path, file_name)

    dict_body = context.api.get_profile_value_key_path(key_path, file_name)
    context.api.prepare_request(body=dict_body)
    context.func.add_formatter_evidence_json(dict_body, "Prepared body")
    context.test_request_body = dict_body


@step(u"prepare the body request")
def prepare_body_data_table(context):
    """
    This step prepares the request body using data table of Gherkin.
    The data dictionary of the json file passed by parameter will be saved in the context
    variable context.test_request_body
    The data table supports two columns, one headed by key and the other by value.
    The data of the body must be listed by key / value
    You can also use values with {{variable}} to reference a json / yaml key from the master file for column value
    :example
        When prepare the body request
          | key      | value  |
          | body1    | valor1 |
          | body1    | valor2 |
    :
    :tag API Prepare Request Steps:
    :param context:
    :return context.test_request_body:
    """
    dict_body = {}
    if context.table:
        for row in context.table:
            if context.func.is_contains_profile_re_var(row["value"]):
                value = context.func.get_formatter_multiple_re_var(row["value"], context.master_file_name_config)
            else:
                value = row["value"]

            dict_body[row["key"]] = value
    context.api.prepare_request(body=dict_body)
    context.func.add_formatter_evidence_json(dict_body, "Prepared body")
    context.test_request_body = dict_body


@step(u"prepare data body request with file name")
def prepare_body_data_table_with_file_name(context):
    """
    This step prepares the request body using data table of Gherkin added another column with profile file name.
    The data dictionary of the json file passed by parameter will be saved in the
    context variable context.test_request_body
    The data table supports third columns, key, value and file_name
    You can also use values with {{variable}} to reference a json / yaml key from the profiles datas

    :example
        When prepare data body request with file name
          | key      | value      | file_name |
          | body1    | valor1     |           |
          | body1    | {{valor2}} | name      |

       Given prepare data body request with file name
          | key            | value               | file_name       |
          | aud            | {{Audience}}        | calendars_datas |
          | sub            | {{Client_UID}}      | calendars_datas |
          | kid            | mule_internet_rs256 |                 |
          | iss            | apic-internet       |                 |
          | cid            | {{CID}}             | calendars_datas |
    :
    :tag API Prepare Request Steps:
    :param context:
    :return context.test_request_body:
    """
    dict_body = {}
    if context.table:
        for row in context.table:
            if row["file_name"] and context.func.is_contains_profile_re_var(row["value"]):
                value = context.func.get_formatter_multiple_re_var(row["value"], row["file_name"])
            else:
                value = row["value"]

            dict_body[row["key"]] = value

    context.api.prepare_request(body=dict_body)
    context.func.add_formatter_evidence_json(dict_body, "Prepared body")
    context.test_request_body = dict_body


@step(u"prepare the method '(?P<method>.+)' request")
def prepare_method(context, method):
    """
    This step prepares the request method passed by parameter.
    The method passed by parameter will be stored in the context variable= context.test_request_method
    You can also use values with {{variable}} to reference a json / yaml key from the master file

    :example
        When prepare the method 'POST' request

        When prepare the method '{{method}}' request

    :
    :tag API Prepare Request Steps:
    :param context:
    :param method:
    :return context.test_request_method:
    """
    if context.func.is_contains_profile_re_var(method):
        method = context.func.get_formatter_multiple_re_var(method, context.master_file_name_config)

    context.api.prepare_request(method=str(method).upper())
    dict_evidence = {"Method": str(method).upper()}
    context.func.add_formatter_evidence_json(dict_evidence, "Prepared method")
    context.test_request_method = str(method).upper()


@step(u"prepare the uri request with key path '(?P<key_path>.+)' in file '(?P<file_name>.+)'")
def prepare_uri_with_key_path_file_name(context, key_path, file_name):
    """
    This step prepares the request uri using a file and key path.
    You have to pass it the path of the file that contains the values of the uri as a json / dictionary and
    and the path of keys to the values of the uri:
    Where the separator character for the key paths will be the period "."
    The uri of the json file passed by parameter will be saved in the context variable context.test_request_uri
    You can also use values with {{variable}} to reference a json / yaml key from the profile file name
    :example
        When prepare the uri request with key path 'api_name.api_example.uri' in file 'api_datas'
    :
    :tag API Prepare Request Steps:
    :param context:
    :param key_path:
    :param file_name:
    :return context.test_request_uri:
    """
    if context.func.is_contains_profile_re_var(key_path):
        key_path = context.func.get_formatter_multiple_re_var(key_path, file_name)
    uri = context.api.get_profile_value_key_path(key_path, file_name)
    context.api.prepare_request(uri=uri)
    dict_evidence = {"URI": str(uri)}
    context.func.add_formatter_evidence_json(dict_evidence, "Prepared Uri")
    context.test_request_uri = str(uri)


@step(u"prepare uri with key '(?P<key_path>.+)' in file '(?P<file_name>.+)' with resource '(?P<uri_path>.+)'")
def prepare_uri_profile_datas(context, key_path, file_name, uri_path):
    """
    This step prepares the request uri using the name of the profile file and the path of
    the key and concatenates the resources of the uri passed by parameter as well
    You have to pass it the name of the profile file that contains the values of the uri as a json / dictionary,
    the path of keys to the values of the uri and the rest of the uri path or resources
    You can also use values with {{variable}} to reference a json / yaml key from the profiles datas
    Where the separator character for the key paths will be the period "."
    The uri of the json file passed by parameter will be saved in the context variable context.test_request_uri
    You can also use values with {{variable}} to reference a json / yaml key from profile file name
    :example
        Given prepare uri with key 'host_server' in file 'profile_datas' with resource '/systems/v1/jwt_tokens'

        Given prepare uri with key 'host_server' in file 'profile_datas' with resource '{{json_key}}/jwt_tokens'
    :
    :tag API Prepare Request Steps:
    :param context:
    :param key_path:
    :param file_name:
    :param uri_path:
    :return context.test_request_uri:
    """
    if file_name and context.func.is_contains_profile_re_var(uri_path):
        uri_path = context.func.get_formatter_multiple_re_var(uri_path, file_name)

    if context.func.is_contains_profile_re_var(key_path):
        key_path = context.func.get_formatter_multiple_re_var(key_path, file_name)

    uri = context.api.get_profile_value_key_path(key_path, file_name)

    if str(uri).endswith("/") and not (str(uri_path).startswith("/")):
        complete_uri = str(uri + uri_path)
    elif not str(uri).endswith("/") and (str(uri_path).startswith("/")):
        complete_uri = str(uri + uri_path)
    elif str(uri).endswith("/") and (str(uri_path).startswith("/")):
        complete_uri = str(uri.rstrip('/') + uri_path)
    else:
        complete_uri = str(uri) + "/" + str(uri_path)
    context.api.prepare_request(uri=complete_uri)
    dict_evidence = {"URI": complete_uri}
    context.func.add_formatter_evidence_json(dict_evidence, "Prepared Uri")
    context.test_request_uri = complete_uri


@step(u"prepare the uri '(?P<uri>.+)' request")
def prepare_uri_by_parameter(context, uri):
    """
    This step prepares the request uri passed by parameter.
    The uri passed by parameter will be stored in the context variable= context.test_request_uri
    You can also use values with {{variable}} to reference a json / yaml key from the master file
    :example
        Given prepare the uri 'https://base-uri/api/client' request
    :
    :tag API Prepare Request Steps:
    :param context:
    :param uri:
    :return context.test_request_uri:
    """
    if context.func.is_contains_profile_re_var(uri):
        uri = context.func.get_formatter_multiple_re_var(uri, context.master_file_name_config)

    context.api.prepare_request(uri=uri)
    dict_evidence = {"URI": str(uri)}
    context.func.add_formatter_evidence_json(dict_evidence, "Prepared Uri")
    context.test_request_uri = str(uri)


@step(u"prepare the uri '(?P<uri>.+)' request with path '(?P<path>.+)'")
def prepare_uri_with_path_by_parameter(context, uri, path):
    """
    This step prepares the request uri passing as a parameter the base uri and the path (s).
    The uri with path passed by parameter will be stored in the context variable= context.test_request_uri
    :example
        Given prepare the uri 'https://base-uri/api/client' request with path '146'

        When prepare the uri 'https://base-uri/api/client' request with path 'jose'

        Scenario Outline:
        Given prepare the uri 'https://base-uri/api/client' request with path '<id>'
            | id    |
            | 146   |
            | 250   |
    :
    :tag API Prepare Request Steps:
    :param context:
    :param uri:
    :param path:
    :return context.test_request_uri:
    """
    if context.func.is_contains_profile_re_var(uri):
        uri = context.func.get_formatter_multiple_re_var(uri, context.master_file_name_config)

    if context.func.is_contains_profile_re_var(path):
        path = context.func.get_formatter_multiple_re_var(path, context.master_file_name_config)

    if str(uri).endswith("/") and not (str(path).startswith("/")):
        complete_uri = str(uri + path)
    elif not str(uri).endswith("/") and (str(path).startswith("/")):
        complete_uri = str(uri + path)
    elif str(uri).endswith("/") and (str(path).startswith("/")):
        complete_uri = str(uri.rstrip('/') + path)
    else:
        complete_uri = str(uri) + "/" + str(path)

    context.api.prepare_request(uri=complete_uri)
    dict_evidence = {"URI": complete_uri}
    context.func.add_formatter_evidence_json(dict_evidence, "Prepared Uri")
    context.test_request_uri = complete_uri


@step(u"prepare the params request with file path '(?P<file_path>.+)'")
def prepare_params_with_file_path(context, file_path):
    """
    This step prepares the request params using a file.
    You have to pass it the path of the file that contains the values of the params as a json / dictionary.
    The data dictionary of the json file passed by parameter will be
    saved in the context variable context.test_request_params
    The file_path parameter allows relative paths
    You can also use values with {{variable}} to reference a json / yaml key from the master file

    :example
        Given prepare the params request with file path 'input/profiles/cer/headers.json'
    :
    :tag API Prepare Request Steps:
    :param context:
    :param file_path:
    :return context.test_request_params:
    """
    if context.func.is_contains_profile_re_var(file_path):
        file_path = context.func.get_formatter_multiple_re_var(file_path, context.master_file_name_config)

    dict_params = dict(files.json_to_dict(file_path))
    context.api.prepare_request(params=dict_params)
    context.func.add_formatter_evidence_json(dict_params, "Prepared params")
    context.test_request_params = dict_params


@step(u"prepare the params request with key path '(?P<key_path>.+)' in file '(?P<file_name>.+)'")
def prepare_params_with_key_file_name(context, key_path, file_name):
    """
    This step prepares the request params using a file and key path.
    You have to pass it the name of the profile file that contains the values of the params as a json / dictionary and
    and the path of keys to the values of the params:
    Where the separator character for the key paths will be the period "."
    Returning a dictionary with the values with the params of the json file
    The data dictionary of the json file passed by parameter will be
    saved in the context variable context.test_request_params
    You can also use values with {{variable}} to reference a json / yaml key from the profile file name

    :example
        When prepare the params request with key path 'api_name.api_example.params' in file 'data_api'
    :
    :tag API Prepare Request Steps:
    :param context:
    :param key_path:
    :param file_name:
    :return context.test_request_params:
    """
    if context.func.is_contains_profile_re_var(key_path):
        key_path = context.func.get_formatter_multiple_re_var(key_path, file_name)
    dict_params = context.api.get_profile_value_key_path(key_path, file_name)
    context.api.prepare_request(params=dict_params)
    context.func.add_formatter_evidence_json(dict_params, "Prepared params")
    context.test_request_params = dict_params


@step(u"prepare the params request")
def prepare_params_data_table(context):
    """
    This step prepares the request params using data table of Gherkin.
    The data dictionary of the json file passed by parameter will be saved in the
    context variable context.test_request_params
    The data table supports two columns, one headed by key and the other by value.
    The data of the params must be listed by param / value
    You can also use values with {{variable}} to reference a json / yaml key from the master file in key_path

    :example
        When prepare the params request
          | param      | value  |
          | param1     | valor1 |
          | param2     | valor2 |

        When prepare the params request
          | param      | value    |
          | param1     | {{key1}} |
          | param2     | valor2   |
    :
    :tag API Prepare Request Steps:
    :param context:
    :return context.test_request_params:
    """
    dict_params = {}
    if context.table:
        for row in context.table:
            if context.func.is_contains_profile_re_var(row["value"]):
                value = context.func.get_formatter_multiple_re_var(row["value"], context.master_file_name_config)
            else:
                value = row["value"]

            dict_params[row["param"]] = value

    context.api.prepare_request(params=dict_params)
    context.func.add_formatter_evidence_json(dict_params, "Prepared params")
    context.test_request_params = dict_params


@step(u"prepare data params request with file name")
def prepare_params_data_table_with_file_name(context):
    """
    This step prepares the request params using data table of Gherkin added another column with profile file name.
    The data dictionary of the json file passed by parameter will be saved in the
    context variable context.test_request_params
    The data table supports third columns, key, value and file_name
    You can also use values with {{variable}} to reference a json / yaml key from the profiles datas

    :example
        When prepare data params request with file name
          | param    | value      | file_name |
          | body1    | valor1     |           |
          | body1    | {{valor2}} | name      |

       Given prepare data body request with file name
          | params            | value               | file_name       |
          | dateFrom          | {{dateFrom}}        | calendars_datas |
          | dateTo            |  2020-01-01         |                 |
          | dateType          | <dateType>          |                 |

    :
    :tag API Prepare Request Steps:
    :param context:
    :return context.test_request_params:
    """
    dict_params = {}
    if context.table:
        for row in context.table:
            if row["file_name"] and context.func.is_contains_profile_re_var(row["value"]):
                value = context.func.get_formatter_multiple_re_var(row["value"], row["file_name"])
            else:
                value = row["value"]

            dict_params[row["param"]] = value

    context.api.prepare_request(params=dict_params)
    context.func.add_formatter_evidence_json(dict_params, "Prepared params")
    context.test_request_params = dict_params


@step(u"set ssl verify value '(?P<ssl>.+)'")
def prepare_ssl(context, ssl):
    """
    This step enables or disables the ssl verification option
    A boolean value must be passed to it=True or False
    the boolean value passed by parameter is stored in the context variable= context.test_request_ssl
    :example
        When set ssl verify value 'True'
    :
    :tag API Prepare Request Steps:
    :param context:
    :param ssl:
    :return context.test_request_ssl:
    """
    dict_evidence = {"SSL": ssl}
    try:
        ssl = bool(str(ssl).lower())
    except Exception as ex:
        print(ex)
        raise ValueError("This step only supports boolean values: True or False")
    context.api.prepare_request(ssl=ssl)
    context.func.add_formatter_evidence_json(dict_evidence, "Prepared ssl")
    context.test_request_ssl = ssl


@step(u"prepare cookies from the previous request")
def prepare_cookies(context):
    """
    This step provides the request with the cookies from the previous execution within the same runtime.
    In order to use this step, a previous request had to be launched first. Then you can
    prepare another request by adding the cookies from the execution of the previous request.
    If this step is launched without a previous request, the cookies will be null
    Cookies will be stored in the context variable= context.test_request_cookies
    :example
        When prepare cookies from the previous request
    :
    :tag API Prepare Request Steps:
    :param context:
    :return context.test_request_cookies:
    """
    context.api.prepare_request(cookies=context.api.cookies)
    context.func.add_formatter_evidence_json(context.api.cookies, "Prepared previous request cookies")
    context.test_request_cookies = context.api.cookies


@step(u"prepare the data payload request with file path '(?P<file_path>.+)'")
def prepare_data_with_file_path(context, file_path):
    """
    This step prepares the request data payload using a file.
    You have to pass it the path of the file that contains the values of the data payload as a json / dictionary.
    The data dictionary of the json file passed by parameter will be saved in the
    context variable context.test_request_payloads
    The file_path parameter allows relative paths
    You can also use values with {{variable}} to reference a json / yaml key from the master file
    :example
        When prepare the data payload request with file path  'datas/datas_payload.json'

        When prepare the data payload request with file path  '{{file_path}}'
    :
    :tag API Prepare Request Steps:
    :param context:
    :param file_path:
    :return context.test_request_payloads:
    """
    if context.func.is_contains_profile_re_var(file_path):
        file_path = context.func.get_formatter_multiple_re_var(file_path, context.master_file_name_config)
    dict_datas = dict(files.json_to_dict(file_path))
    context.api.prepare_request(data=dict_datas)
    context.func.add_formatter_evidence_json(dict_datas, "Prepared data payload")
    context.test_request_payloads = dict_datas


@step(u"prepare the data payload request with key path '(?P<key_path>.+)' in file '(?P<file_name>.+)'")
def prepare_data_with_path_key(context, key_path, file_name):
    """
    This step prepares the request data payload using a file and key path.
    You have to pass it the name of the profile file that contains the values of the
    data payload as a json / dictionary and
    and the path of keys to the values of the data payload:
    Where the separator character for the key paths will be the period "."
    Returning a dictionary with the values with the data payload of the json file
    The data dictionary of the json file passed by parameter will be
    saved in the context variable context.test_request_payloads
    You can also use values with {{variable}} to reference a json / yaml key from the profile file name
    :example
        When prepare the data payload request with key path 'api_name.api_example.headers' in file 'api_data'
    :
    :tag API Prepare Request Steps:
    :param context:
    :param key_path:
    :param file_name:
    :return context.test_request_payloads:
    """

    if context.func.is_contains_profile_re_var(key_path):
        key_path = context.func.get_formatter_multiple_re_var(key_path, file_name)

    dict_datas = context.api.get_profile_value_key_path(key_path, file_name)
    context.api.prepare_request(data=dict_datas)
    context.func.add_formatter_evidence_json(dict_datas, "Prepared data payload")
    context.test_request_payloads = dict_datas


@step(u"prepare the data payload request")
def prepare_data_with_data_table(context):
    """
    This step prepares the request data payload using data table of Gherkin.
    The data dictionary of the json file passed by parameter will be
    saved in the context variable context.test_request_payloads
    The data table supports two columns, one headed by key and the other by value.
    The data of the data payload must be listed by key / value
    You can also use values with {{variable}} to reference a json / yaml key from the master file
    :example
        When prepare the data payload request
          | key     | value    |
          | data1   | valor1   |
          | datas2  | {{key2}} |
    :
    :tag API Prepare Request Steps:
    :param context:
    :return context.test_request_payloads:
    """
    dict_datas = {}
    if context.table:
        for row in context.table:
            if context.func.is_contains_profile_re_var(row["value"]):
                value = context.func.get_formatter_multiple_re_var(row["value"], context.master_file_name_config)
            else:
                value = row["value"]

            dict_datas[row["key"]] = value
    context.api.prepare_request(data=dict_datas)
    context.func.add_formatter_evidence_json(dict_datas, "Prepared data payload")
    context.test_request_payloads = dict_datas


#: TODO: terminar este step
@step(u"prepare the data payload form request")
def prepare_data_payload_string(context):
    """
    With this step the body payload is prepared by passing it a string from a form in a data table whose
    header must be "value"
    :example
        given prepare the data payload form request
        |   value           |
        |   a_form_string   |
    :
    :tag API Prepare Request Steps:
    :param context:
    :return context.test_request_payloads:
    """
    payload = ''
    if context.table:
        for row in context.table:
            payload = row['value']

    context.api.prepare_request(data=payload)
    context.func.add_formatter_evidence_json({'value': payload}, "Prepared data payload")
    context.test_request_payloads = {'value': payload}


@step(u"prepare the multiple files request")
def prepare_multiple_files(context):
    """
    This step prepares files that have to be attached to the request using a Gherkin data table
    A tuple will be generated that will store a dictionary for each file that is needed
    This tuple will be stored in the context variable= context.test_request_files
    The headers of the table are mandatory and must be=field_name, file_path, file_info
    where field_name is the name of the file field, file_path, the path of the file (can be relative),
    file_info, the file information and file type
    You can also use values with {{variable}} to reference a json / yaml key from the master file
    :example
        When prepare the multiple files request
          | field_name      | file_path     | file_info   |
          | images          | foo.png       | image/png   |
          | {{field}}       | {{path}}      | {{type}}    |
    :
    :tag API Prepare Request Steps:
    :param context:
    :return context.test_request_files:
    """
    files_list = []
    evidence_dict = {}
    cont = 1
    if context.table:
        for row in context.table:
            field_name = row["field_name"]
            file_path = row["file_path"]
            file_info = row["file_info"]
            if context.func.is_contains_profile_re_var(field_name):
                field_name = context.func.get_formatter_multiple_re_var(field_name, context.master_file_name_config)

            if context.func.is_contains_profile_re_var(file_path):
                file_path = context.func.get_formatter_multiple_re_var(file_path, context.master_file_name_config)

            if context.func.is_contains_profile_re_var(file_info):
                file_info = context.func.get_formatter_multiple_re_var(file_info, context.master_file_name_config)

            file_tuple = (field_name, (field_name, open(file_path, "rb"), file_info))
            files_list.append(file_tuple)
            evidence_dict["Tuple Data " + str(cont)] = {"Field name": field_name,
                                                        "File path": file_path,
                                                        "File info": file_info}
            cont += 1
    context.api.prepare_request(files=files_list)
    context.func.add_formatter_evidence_json(evidence_dict, "Prepared Multiple Files")
    context.test_request_files = evidence_dict


@step(u"prepare the test_files request")
def prepare_files(context):
    """
    This step attaches a single file to the request using a Gherkin data table
    A dictionary is generated with the information from the data table file that is stored
    in the context variable= context.test_request_files
    The headers must be=field_name (field name or file type) and file_path (file path, it can be relative path)
    You can also use values with {{variable}} to reference a json / yaml key from the master file
    :example
        When prepare the test_files request
          | field_name | file_path |
          | images     | foo.png   |
          | file       | foo.txt   |
    :
    :tag API Prepare Request Steps:
    :param context:
    :return context.test_request_files:
    """
    files_dist = {}
    test_files = {}
    if context.table:
        for row in context.table:
            field_name = row["field_name"]
            file_path = row["file_path"]
            if context.func.is_contains_profile_re_var(field_name):
                field_name = context.func.get_formatter_multiple_re_var(field_name, context.master_file_name_config)

            if context.func.is_contains_profile_re_var(file_path):
                file_path = context.func.get_formatter_multiple_re_var(file_path, context.master_file_name_config)

            test_files = {field_name: open(file_path, "rb")}
            files_dist["Field name"] = field_name
            files_dist["Field path"] = file_path

    context.api.prepare_request(files=test_files)
    context.func.add_formatter_evidence_json(files_dist, "Prepared Files")
    context.test_request_files = test_files


#######################################################################################################################
#                                            Verifications Steps                                                      #
#######################################################################################################################
@step(u"verify simple value '(?P<value>.+)' of type '(?P<value_type>.+)' in key '(?P<key>.+)'")
def verify_step_simple_value(context, value, value_type, key):
    """
    This step verifies if the current value of a key passed by
    parameter is of type and is equal to an expected value passed by parameter
    For the data type it allows the values=int (integer), bool (boolean), float (float) and none (null)
    You can also use values with {{variable}} to reference a json / yaml key from the master file
    :example
        Then verify simple value '142' of type 'int' in key 'client_id'

        Then verify simple value 'hello word' of type 'str' in key 'a_key'
    :
    :tag API Verifications Steps:
    :param context:
    :param value:
    :param value_type:
    :param key:
    :return:
    """
    if context.func.is_contains_profile_re_var(value):
        value = context.func.get_formatter_multiple_re_var(value, context.master_file_name_config)

    if value_type == "int" or value_type == "integer":
        value = int(value)
    elif value_type == "bool" or value_type == "boolean":
        value = bool(value)
    elif value_type == "float":
        value = float(value)
    elif value_type == "none" or value_type == "null":
        value = None
    context.api.verify_simple_value_in_response(key, value, context.response)


@step(u"verify value '(?P<value>.+)' of type '(?P<value_type>.+)' in path key '(?P<key>.+)'")
def verify_step_value_in_path_key(context, value, value_type, key):
    """
    This step checks if the current value of a key path passed by the parameter is
    of type and equals an expected value passed by parameter of the response
    Where the separator character for the key paths will be the period "."
    For the data type it allows the values= int (integer), bool (boolean), float (float) and none (null)
    You can also use values with {{variable}} to reference a json / yaml key from the master file

    :example
        Then verify value '142' of type 'int' in path key 'clients.client_id'

        Then verify value 'josé' of type 'str' in path key 'clients.name'
    :
    :tag API Verifications Steps:
    :param context:
    :param value:
    :param value_type:
    :param key:
    :return:
    """
    if context.func.is_contains_profile_re_var(value):
        value = context.func.get_formatter_multiple_re_var(value, context.master_file_name_config)

    if value_type == "int" or value_type == "integer":
        value = int(value)
    elif value_type == "bool" or value_type == "boolean":
        value = bool(value)
    elif value_type == "float":
        value = float(value)
    elif value_type == "none" or value_type == "null":
        value = None
    context.api.verify_value_in_response_with_path(key, value, context.response)


@step(u"validate the response scheme with the json file in the path '(?P<file_path>.+)'")
def verify_schema_file_path(context, file_path):
    """
    This step verifies the current schema of the response with the schema expected from a file passing the file path
    You can also use values with {{variable}} to reference a json / yaml key from the master file
    :example
        Then validate the response scheme with the json file in the path 'files/schema.json'
    :
    :tag API Verifications Steps:
    :param context:
    :param file_path:
    :return:
    """
    if context.func.is_contains_profile_re_var(file_path):
        file_path = context.func.get_formatter_multiple_re_var(file_path, context.master_file_name_config)
    expected_schema = files.json_to_dict(file_path)
    context.api.validate_json_schema(expected_schema)


@step(u"validate the response scheme with the key path '(?P<key_path>.+)' in file '(?P<file_name>.+)'")
def verify_schema_key_context(context, key_path, file_name):
    """
    This step verifies that the expected schema located in a path of keys and in a
    file profile name passed by parameter is equal to the current schema of the response
    You can also use values with {{variable}} to reference a json / yaml key from the profile file name

    :example
        Then validate the response scheme with the key path 'api_name.schema' in file 'apis'
    :
    :tag API Verifications Steps:
    :param context:
    :param key_path:
    :param file_name:
    :return:
    """
    if context.func.is_contains_profile_re_var(key_path):
        key_path = context.func.get_formatter_multiple_re_var(key_path, file_name)
    expected_schema = context.api.get_profile_value_key_path(key_path, file_name)
    context.api.validate_json_schema(expected_schema)


@step(u"validate the response scheme with the key path '(?P<key_path>.+)' in file path '(?P<file_path>.+)'")
def verify_schema_key_path_file_path(context, key_path, file_path):
    """
    This step verifies that the expected schema located in a path of keys and in a
    file with path  passed by parameter is equal to the current schema of the response
    You can also use values with {{variable}} to reference a json / yaml key from the master file
    :example
        Then validate the response scheme with the key path 'api.token' in file path 'datas/api.json'

        Then validate the response scheme with the key path '{{key_path}}' in file path '{{file path}}'
    :
    :tag API Verifications Steps:
    :param context:
    :param key_path:
    :param file_path:
    :return:
    """
    if context.func.is_contains_profile_re_var(key_path):
        key_path = context.func.get_formatter_multiple_re_var(key_path, context.master_file_name_config)

    if context.func.is_contains_profile_re_var(file_path):
        file_path = context.func.get_formatter_multiple_re_var(file_path, context.master_file_name_config)

    expected_schema = files.get_json_value_key_path(key_path, file_path)
    context.api.validate_json_schema(expected_schema, input_type="json")


@step(u"remove the '(?P<value>.+)' value from the request params")
def remove_value_from_param(context, value):
    """
    This step removes a parameter from the request params already set earlier.
    The key of the params that you want to delete is passed as a parameter.
    :example
        When remove the 'param1' value from the request params
    :
    :param context:
    :param value:
    :return:
    """
    evidence_dict = {
        "headers deleted": {
            "key": value,
            "value": context.api.params[value]
        }
    }
    del context.api.params[value]
    context.func.add_formatter_evidence_json(evidence_dict, "delete param value")


@step(u"remove the '(?P<value>.+)' value from the request headers")
def remove_value_from_headers(context, value):
    """
    This step removes a parameter from the request header already set earlier.
    The key of the header that you want to delete is passed as a parameter.
    :example
        When remove the 'Authorization' value from the request headers
    :
    :param context:
    :param value:
    :return:
    """
    evidence_dict = {
        "headers deleted": {
            "key": value,
            "value": context.api.headers[value]
        }
    }

    del context.api.headers[value]

    context.func.add_formatter_evidence_json(evidence_dict, "delete header value")


@step(u"remove the value with key path '(?P<key_path>.+)' from the request body")
def remove_value_from_body(context, key_path):
    """
    This step removes a key from the request body already set earlier from a key path.
    The key of the body that you want to delete is passed as a parameter,
    you can pass a key path dot separated as well.
    :example
         When remove the value with key path 'items.properties' from the request body

         When remove the value with key path 'items' from the request body

    :
    :param context:
    :param key_path:
    :return:
    """
    *path, key = key_path.split('.')

    evidence_dict = {
        "body deleted": {
            "key": str(key),
            "value": str(path)
        }
    }

    reduction = reduce(operator.getitem, path, context.api.body)
    if isinstance(reduction, list):
        for item in reduction:
            del item[key]
    else:
        del reduction[key]
    context.func.add_formatter_evidence_json(evidence_dict, "delete body value")


@step(u"change the value with key path '(?P<key_path>.+)' to null from the request body")
def change_value_from_body(context, key_path):
    """
    This step changes a key from the request body already set earlier from a key path.
    The key of the body that you want to delete is passed as a parameter,
    you can pass a key path dot separated as well.
    :example
         When change the value with key path 'items.properties' to null from the request body

    :
    :param context:
    :param key_path:
    :return:
    """
    *path, key = key_path.split('.')

    evidence_dict = {
        "body deleted": {
            "key": str(key),
            "value": str(path),
        }
    }
    reduction = reduce(operator.getitem, path, context.api.body)
    if isinstance(reduction, list):
        for item in reduction:
            item[key] = None
    else:
        reduction[key] = None
    context.func.add_formatter_evidence_json(evidence_dict, "change body value")


@step(u"validate response schema with key path and file name in table")
def verify_schema_key_context_in_table(context):
    """
    This step verifies that the expected schema located in a path of keys and in a
    file profile name passed by data table is equal to the current schema of the response
    The data table must have the columns=key_path and file_name.
    Only one schema is accepted, that is, the data table can only have one row with a key path and a file path
    :example
        And validate response schema with key path and file name in table
          | key_path              | file_name  |
          | api-services.schema_3 | datas      |
    :
    :tag API Verifications Steps:
    :param context:
    :return:
    """
    key_path = ""
    file_name = ""
    if context.table:
        for row in context.table:
            key_path = row["key_path"]
            file_name = row["file_name"]
            if context.func.is_contains_profile_re_var(key_path):
                key_path = context.func.get_formatter_multiple_re_var(key_path, file_name)
    expected_schema = context.api.get_profile_value_key_path(key_path, file_name)
    context.api.validate_json_schema(expected_schema)


@step(u"validate response schema with key path and file path")
def verify_schema_key_context_key_path_file_path(context):
    """
    This step verifies that the expected schema located in a path of keys and in a
    file path name passed by data table is equal to the current schema of the response
    The data table must have the columns=key_path and file_name.
    Only one schema is accepted, that is, the data table can only have one row with a key path and a file path
    You can also use values with {{variable}} to reference a json / yaml key from profile file name

    :example
        And validate response schema with key path and file path
          | key_path              | file_path                       |
          | api-services.schema_3 | datas/calendars_validations.json |
    :
    :tag API Verifications Steps:
    :param context:
    :return:
    """
    key_path = ""
    file_path = ""

    if context.table:
        for row in context.table:
            key_path = row["key_path"]
            file_path = row["file_path"]
            if context.func.is_contains_profile_re_var(key_path):
                key_path = context.func.get_formatter_multiple_re_var(key_path, context.master_file_name_config)
            if context.func.is_contains_profile_re_var(file_path):
                file_path = context.func.get_formatter_multiple_re_var(file_path, context.master_file_name_config)
    expected_schema = files.get_json_value_key_path(key_path, file_path)
    context.api.validate_json_schema(expected_schema, input_type="json")


@step(u"validate schema: key '(?P<key_path>.+)', file name '(?P<file_name>.+)'")
def verify_schema_key_context_key_path_filename_parameter(context, key_path, file_name):
    """
    This step verifies that the expected schema located in a path of keys and in a
    file profile name passed by parameter is equal to the current schema of the response
    You can also use values with {{variable}} to reference a json / yaml key from profile file name
    :example
        Then validate schema: key 'api-services.schema_3', file name 'api'
    :
    :tag API Verifications Steps:
    :param context:
    :param key_path:
    :param file_name:
    :return:
    """
    if context.func.is_contains_profile_re_var(key_path):
        key_path = context.func.get_formatter_multiple_re_var(key_path, context.master_file_name_config)
    expected_schema = context.api.get_profile_value_key_path(key_path, file_name)
    context.api.validate_json_schema(expected_schema)


@step(u"verify response contains value '(?P<value>.+)' of type '(?P<value_type>.+)'")
def verify_contains_path_value(context, value, value_type):
    """
    This step verifies that the response contains an expected value and data type
    You can also use values with {{variable}} to reference a json / yaml key from the master file
    :example
        Then verify response contains value '134' of type 'int'

        Then verify response contains value 'jose' of type 'str'
    :
    :tag API Verifications Steps:
    :param context:
    :param value:
    :param value_type:
    :return:
    """
    if context.func.is_contains_profile_re_var(value):
        value = context.func.get_formatter_multiple_re_var(value, context.master_file_name_config)
    if value_type == "int" or value_type == "integer":
        value = int(value)
    elif value_type == "bool" or value_type == "boolean":
        value = bool(value)
    elif value_type == "float":
        value = float(value)
    elif value_type == "none" or value_type == "null":
        value = None

    context.api.verify_response_contains_value(value, context.response)


@step(u"verify response contains value '(?P<value>.+)'")
def verify_response_contains_value(context, value):
    """
    This step verifies that the response contains a value by specifying by parameter
    You can also use values with {{variable}} to reference a json / yaml key from the master file
    :example
        And verify response contains value '<error_value>' of type 'string'
    :
    :tag API Verifications Steps:
    :param context:
    :param value:
    :return:
    """
    if context.func.is_contains_profile_re_var(value):
        value = context.func.get_formatter_multiple_re_var(value, context.master_file_name_config)
    context.api.verify_response_contains_value(value)


@step(u"verify response headers contains value '(?P<value>.+)' of type '(?P<value_type>.+)'")
def verify_contains_headers_value(context, value, value_type):
    """
    This step verifies that the headers response contains an expected value and data type
    :example
        Then verify response headers contains value 'text/html' of type 'str'

        Then verify response contains value '0.088190' of type 'float'
    :
    :tag API Verifications Steps:
    :param context:
    :param value:
    :param value_type:
    :return:
    """
    if context.func.is_contains_profile_re_var(value):
        value = context.func.get_formatter_multiple_re_var(value, context.master_file_name_config)
    if value_type == "int" or value_type == "integer":
        value = int(value)
    elif value_type == "bool" or value_type == "boolean":
        value = bool(value)
    elif value_type == "float":
        value = float(value)
    elif value_type == "none" or value_type == "null":
        value = None

    context.api.verify_response_headers_contains_value(value, context.response)


@step(u"verify status reason is '(?P<reason>.+)'")
def verify_reason(context, reason):
    """
    This step verifies that the current reason is equal to the expected one passed by parameter
    :example
        Then verify status reason is 'OK'
    :
    :tag API Verifications Steps:
    :param context:
    :param reason:
    :return:
    """
    context.api.verify_response_reason(reason, context.response)


@step(u"verify the value of the key '(?P<key>.+)' is of type '(?P<value_type>.+)'")
def verify_contains_value_type_key(context, key, value_type):
    """
    This step verifies that the value of the key passed by parameter is of the indicated type
    The allowed data types are = int (integer), str (string), bool (boolean), float, dict (dictionary),
    list, tuple, array and none (null)
    :example
        Then verify the value of the key 'client_id' is of type 'int'

        Then verify the value of the key 'datas_payload' is of type 'dict'
    :
    :tag API Verifications Steps:
    :param context:
    :param key:
    :param value_type:
    :return:
    """

    if value_type == "int" or value_type == "integer":
        value_type = int
    if value_type == "str" or value_type == "string":
        value_type = str
    elif value_type == "bool" or value_type == "boolean":
        value_type = bool
    elif value_type == "float":
        value_type = float
    elif value_type == "dict" or value_type == "dictionary":
        value_type = dict
    elif value_type == "list":
        value_type = list
    elif value_type == "tuple":
        value_type = tuple
    elif value_type == "array":
        value_type = array
    elif value_type == "none" or value_type == "null":
        value_type = None

    context.api.verify_response_value_type(key, value_type, context.response)


@step(u"verify status code is '(?P<status_code>.+)'")
def verify_step_status_code(context, status_code):
    """
    This step verifies that the current status code is equal to the expected one passed by parameter
    :example
        Then verify status code is '200'
    :
    :tag API Verifications Steps:
    :param context:
    :param status_code:
    :return:
    """
    try:
        status_code = int(status_code)
    except ValueError as ex:
        print(ex)
        raise ValueError('The status code must be a three digit integer, for example: \"200\", \"300\", \"500\"')
    context.api.verify_status_code(status_code, context.response)


@step(u"verify type value '(?P<value_type>.+)' in path key '(?P<key>.+)'")
def verify_type_value_in_path_key(context, value_type, key):
    """
    This step verifies that the value of the path key passed by parameter is of the indicated type
    Where the separator character for the key paths will be the period "."
    The allowed data types are -  int (integer), bool (boolean), float, dict (dictionary),
    list, tuple, array and none (null)
    You can also use values with {{variable}} to reference a json / yaml key from the master file
    :example
        Then verify the value of the key 'clients.client_id' is of type 'int'

        Then verify the value of the key 'datas.datas_payload' is of type 'dict'
    :
    :tag API Verifications Steps:
    :param context:
    :param key:
    :param value_type:
    :return:
    """
    if value_type == "str":
        value_type = str
    elif value_type == "int":
        value_type = int
    elif value_type == "int":
        value_type = int
    elif value_type == "bool":
        value_type = bool
    elif value_type == "dict":
        value_type = dict
    elif value_type == "float":
        value_type = float
    else:
        raise Exception(str(value_type) + " is not a valid data type")

    if context.func.is_contains_profile_re_var(key):
        key = context.func.get_formatter_multiple_re_var(key, context.master_file_name_config)
    context.api.verify_value_type_in_response_with_path(key, value_type, context.response)


@step(u"verify response headers contains '(?P<headers>.+)'")
def verify_response_headers_contains(context, headers):
    """
    This step verifies that the response headers contain the value passed by parameter
    You can also use values with {{variable}} to reference a json / yaml key from the master file
    :example
        Then verify response headers contains 'text/html'
    :
    :tag API Verifications Steps:
    :param context:
    :param headers:
    :return:
    """
    if context.func.is_contains_profile_re_var(headers):
        headers = context.func.get_formatter_multiple_re_var(headers, context.master_file_name_config)
    context.api.verify_response_headers_contains_value(headers)


@step(u"verify response contains key '(?P<key>.+)'")
def verify_response_contains_keys(context, key):
    """
    This step verifies that the response contains a specific key passed by parameter
    :example
        And verify response contains key 'Authorization'
    :
    :tag API Verifications Steps:
    :param context:
    :param key:
    :return:
    """
    context.api.verify_response_contains_key(key, response=context.response)


@step(u"verify status code is one of '(?P<status_code>.+)'")
def verify_status_code_ins_one_of(context, status_code):
    """
    This step verifies that the current status code is equal to the
    expected one passed by parameter as a comma-separated list
    :example
        And verify status code is one of '200, 201, 202'
    :
    :tag API Verifications Steps:
    :param context:
    :param status_code:
    :return:
    """
    status_code_list = []
    try:
        split_status_code = str(status_code).split(",")
        for value in split_status_code:
            status_code_list.append(int(value))
    except ValueError as ex:
        print(ex)
        raise ValueError('The status codes must be a three digit integer, for example: \"200\", \"300\", \"404\"')

    context.api.status_code_is_one_of(status_code_list, context.response)


@step(u"verify response time is between '(?P<less_expected>.+)' and '(?P<greater_expected>.+)'")
def verify_response_time_is_between(context, less_expected, greater_expected):
    """
    This step verifies that the response time is between a minimum expected time and a maximum expected time
    Expected times can be in both integers and float
    :example
        Then verify response time is between '0.01' and '2.503'
    :
    :tag API Verifications Steps:
    :param context:
    :param less_expected:
    :param greater_expected:
    :return:
    """
    try:
        less_expected = float(less_expected)
        greater_expected = float(greater_expected)
    except Exception as ex:
        print(ex)
        raise Exception('Time values must be integers or floats, for example: \"1\" or \"20.503\"')

    context.api.response_time_is_between(less_expected, greater_expected, context.response)


@step(u"verify response time is less than '(?P<second_expected>.+)'")
def verify_response_time_less(context, second_expected):
    """
    This step allows you to verify if the response time is less than the expected value
    The expected time can be in integers or float
    :example
        Then verify response time is less than '2.503'
    :
    :tag API Verifications Steps:
    :param context:
    :param second_expected:
    :return:
    """
    try:
        second_expected = float(second_expected)
    except Exception as ex:
        print(ex)
        raise Exception('Time values must be integers or floats, for example: \"1\" or \"20.503\"')
    context.api.response_time_is_less_than(second_expected, context.response)


@step(u"verify response time is greater than '(?P<second_expected>.+)'")
def verify_response_time_is_greater(context, second_expected):
    """
    This step allows you to verify if the response time is greater than the expected value
    The expected time can be in integers or float
    :example
        Then verify response time is greater than '0.01'
    :
    :tag API Verifications Steps:
    :param context:
    :param second_expected:
    :return
    """
    try:
        second_expected = float(second_expected)
    except Exception:
        raise Exception('Time values must be integers or floats, for example: \"1\" or \"20.503\"')
    context.api.response_time_is_greater_than(second_expected, context.response)


#######################################################################################################################
#                                               Authorization Steps                                                   #
#######################################################################################################################
@step(u"create basic authorization")
def create_basic_authorization(context):
    """
    This step creates and prepares on request a basic authorization using a Gherkin data table
    You can also use values with {{variable}} to reference a json / yaml key from the master file
    :example
        Given create basic authorization
            | username | password |
            | user     | pass     |
    :
    :tag API Authorization Steps:
    :param context:
    :return:
    """
    data_dict = {}
    if context.table:
        for headers in context.table.headings:
            for row in context.table:
                data_dict[headers] = row[headers]

    username = data_dict["username"]
    password = data_dict["password"]
    if context.func.is_contains_profile_re_var(username):
        username = context.func.get_formatter_multiple_re_var(username, context.master_file_name_config)
    if context.func.is_contains_profile_re_var(password):
        password = context.func.get_formatter_multiple_re_var(password, context.master_file_name_config)
    context.test_basic_auth = context.api.create_basic_authorization(username, password)
    context.api.prepare_request(authorization=context.test_basic_auth)
    context.func.add_formatter_evidence_json(data_dict, "Prepared basic authorization")


@step(u"create basic authorization with username '(?P<username>.+)' and password '(?P<password>.+)'")
def create_basic_authorization_with(context, username, password):
    """
     This step creates and prepares on request a basic authorization
     using username and password passed by parameter
     You can also use values with {{variable}} to reference a json / yaml key from the master file
     :example
        Given create basic authorization with username 'username' and password 'password'
    :
    :tag API Authorization Steps:
    :param context:
    :param username:
    :param password:
    :return:
    """
    if context.func.is_contains_profile_re_var(username):
        username = context.func.get_formatter_multiple_re_var(username, context.master_file_name_config)
    if context.func.is_contains_profile_re_var(password):
        password = context.func.get_formatter_multiple_re_var(password, context.master_file_name_config)
    context.test_basic_auth = context.api.create_basic_authorization(username, password)
    context.api.prepare_request(authorization=context.test_basic_auth)
    context.func.add_formatter_evidence_json({"username": username, "password": password},
                                             "Prepared basic authorization")


@step(u"create digest authorization")
def create_digest_authorization(context):
    """
    This step creates and prepares on request a digest authorization using a Gherkin data table
    You can also use values with {{variable}} to reference a json / yaml key from the master file

    :example
        Given create digest authorization
            | username | password |
            | user     | pass     |
    :
    :tag API Authorization Steps:
    :param context:
    :return:
    """
    data_dict = {}
    if context.table:
        for headers in context.table.headings:
            for row in context.table:
                data_dict[headers] = row[headers]

    username = data_dict["username"]
    password = data_dict["password"]

    if context.func.is_contains_profile_re_var(username):
        username = context.func.get_formatter_multiple_re_var(username, context.master_file_name_config)
    if context.func.is_contains_profile_re_var(password):
        password = context.func.get_formatter_multiple_re_var(password, context.master_file_name_config)
    context.test_digest_auth = context.api.create_basic_authorization(username, password,
                                                                      auth_type="digest")
    context.api.prepare_request(authorization=context.test_digest_auth)
    context.func.add_formatter_evidence_json(data_dict, "Prepared digest authorization")


@step(u"create digest authorization with username '(?P<username>.+)' and password '(?P<password>.+)'")
def create_digest_authorization_with(context, username, password):
    """
     This step creates and prepares on request a digest authorization using username and password passed by parameter
     You can also use values with {{variable}} to reference a json / yaml key from the master file

     :example
        Given create digest authorization with username 'username' and password 'password'
    :
    :tag API Authorization Steps:
    :param context:
    :param username:
    :param password:
    :return:
    """
    if context.func.is_contains_profile_re_var(username):
        username = context.func.get_formatter_multiple_re_var(username, context.master_file_name_config)
    if context.func.is_contains_profile_re_var(password):
        password = context.func.get_formatter_multiple_re_var(password, context.master_file_name_config)
    context.test_digest_auth = context.api.create_basic_authorization(username, password, auth_type="digest")
    context.api.prepare_request(authorization=context.test_digest_auth)
    context.func.add_formatter_evidence_json({"username": username, "password": password},
                                             "Prepared digest authorization")


@step(u"create oauth1 authorization")
def create_oauth1_authorization(context):
    """
    This step creates and prepares on request an oauth1 authorization using a gherkin data table
    The table should have the headings of=app_key, app_secret, user_oauth_token and user_oauth_token_secret
    You can also use values with {{variable}} to reference a json / yaml key from the master file
    :example
        Given create oauth1 authorization
            | app_key | app_secret |user_oauth_token |user_oauth_token_secret |
            | key     | secret     |token            |token secret            |
    :
    :tag API Authorization Steps:
    :param context:
    :return:
    """
    data_dict = {}
    if context.table:
        for headers in context.table.headings:
            for row in context.table:
                data_dict[headers] = row[headers]

    app_key = data_dict["app_key"]
    app_secret = data_dict["app_secret"]
    user_oauth_token = data_dict["user_oauth_token"]
    user_oauth_token_secret = data_dict["user_oauth_token_secret"]

    if context.func.is_contains_profile_re_var(app_key):
        app_key = context.func.get_formatter_multiple_re_var(app_key, context.master_file_name_config)
    if context.func.is_contains_profile_re_var(app_secret):
        app_secret = context.func.get_formatter_multiple_re_var(app_secret, context.master_file_name_config)
    if context.func.is_contains_profile_re_var(user_oauth_token):
        user_oauth_token = context.func.get_formatter_multiple_re_var(user_oauth_token, context.master_file_name_config)
    if context.func.is_contains_profile_re_var(user_oauth_token_secret):
        user_oauth_token_secret = context.func.get_formatter_multiple_re_var(user_oauth_token_secret,
                                                                             context.master_file_name_config)

    context.test_oauth1_auth = context.api.create_oauth1(app_key,
                                                         app_secret,
                                                         user_oauth_token,
                                                         user_oauth_token_secret)
    context.api.prepare_request(authorization=context.test_oauth1_auth)
    context.func.add_formatter_evidence_json(data_dict, "Prepared oauth1 authorization")


@step(u"create oauth2 authorization")
def create_oauth2_authorization(context):
    """
    This step creates and prepares on request a oauth2 authorization using a Gherkin data table
    The table should have the headings of=flow, client_id, client_secret, url and scope
    Where the value of flow must be=web, mobile, legacy or backend
    :example
        Given create oauth2 authorization
            | flow     | client_id           | client_secret       | url          | scope       |
            | web      | client_id_value     | client_secret_value | url_value    | scope_value |
            | mobile   | client_id_value     |                     | url_value    | scope_value |
            | legacy   | client_id_value     |                     |              |             |
            | backend  | client_id_value     |                     |              |             |
    :
    :tag API Authorization Steps:
    :param context:
    :return:
    """
    data_dict = {}
    if context.table:
        for headers in context.table.headings:
            for row in context.table:
                data_dict[headers] = row[headers]

    client_id = data_dict["client_id"]
    client_secret = data_dict["client_secret"]
    url = data_dict["url"]
    scope = data_dict["scope"]

    if context.func.is_contains_profile_re_var(client_id):
        client_id = context.func.get_formatter_multiple_re_var(client_id, context.master_file_name_config)
    if context.func.is_contains_profile_re_var(client_secret):
        client_secret = context.func.get_formatter_multiple_re_var(client_secret, context.master_file_name_config)
    if context.func.is_contains_profile_re_var(url):
        url = context.func.get_formatter_multiple_re_var(url, context.master_file_name_config)
    if context.func.is_contains_profile_re_var(scope):
        scope = context.func.get_formatter_multiple_re_var(scope, context.master_file_name_config)

    try:
        flow = data_dict["flow"]

    except Exception as ex:
        raise Exception("Value flow is mandatory: \n" + str(ex))

    if context.func.is_contains_profile_re_var(flow):
        flow = context.func.get_formatter_multiple_re_var(flow, context.master_file_name_config)

    if flow == "web":
        context.test_oauth2_auth = context.api.create_oauth2(flow, client_id, client_secret, url, scope)
    elif flow == "mobile":
        context.test_oauth2_auth = context.api.create_oauth2(flow, client_id, url, scope)
    elif flow == "legacy" or flow == "backend":
        context.test_oauth2_auth = context.api.create_oauth2(flow, client_id)

    context.api.prepare_request(authorization=context.test_oauth2_auth)
    context.func.add_formatter_evidence_json(data_dict, "Prepared oauth2 authorization")


@step(u"create mobile oauth2 authorization with client id '(?P<cid>.+)', url '(?P<url>.+)' and scope '(?P<scope>.+)'")
def create_oauth2_mobile_authorization(context, cid, url, scope):
    """
    This step creates and prepares on request an mobile oauth2 authorization passed by parameter
    You can also use values with {{variable}} to reference a json / yaml key from the master file
    :example
        Given create mobile oauth2 authorization with client id 'client_id', url 'url' and scope 'scope'
    :
    :tag API Authorization Steps:
    :param context:
    :param cid:
    :param url:
    :param scope:
    :return:
    """
    if context.func.is_contains_profile_re_var(cid):
        cid = context.func.get_formatter_multiple_re_var(cid, context.master_file_name_config)
    if context.func.is_contains_profile_re_var(url):
        url = context.func.get_formatter_multiple_re_var(url, context.master_file_name_config)
    if context.func.is_contains_profile_re_var(scope):
        scope = context.func.get_formatter_multiple_re_var(scope, context.master_file_name_config)

    context.test_oauth2_auth = context.api.create_oauth2(flow="mobile", client_id=cid, url=url, scope=scope)
    data_dict = {
        "flow": "mobile",
        "client_id": cid,
        "url": url,
        "scope": scope
    }
    context.api.prepare_request(authorization=context.test_oauth2_auth)
    context.func.add_formatter_evidence_json(data_dict, "Prepared oauth2 authorization")


@step(u"create legacy oauth2 authorization with client id '(?P<client_id>.+)'")
def create_oauth2_legacy_authorization(context, client_id):
    """
    This step creates and prepares on request an legacy oauth2 authorization passed by parameter
    You can also use values with {{variable}} to reference a json / yaml key from the master file
    :example
        Given create legacy oauth2 authorization with client id 'client_id'
    :
    :tag API Authorization Steps:
    :param context:
    :param client_id:
    :return:
    """
    if context.func.is_contains_profile_re_var(client_id):
        client_id = context.func.get_formatter_multiple_re_var(client_id, context.master_file_name_config)
    context.test_oauth2_auth = context.api.create_oauth2(flow="legacy", client_id=client_id)
    data_dict = {
        "flow": "legacy",
        "client_id": client_id
    }
    context.api.prepare_request(authorization=context.test_oauth2_auth)
    context.func.add_formatter_evidence_json(data_dict, "Prepared oauth2 authorization")


@step(u"create backend oauth2 authorization with client id '(?P<client_id>.+)'")
def create_oauth2_backend_authorization(context, client_id):
    """
    This step creates and prepares on request an backend oauth2 authorization passed by parameter
    You can also use values with {{variable}} to reference a json / yaml key from the master file
    :example
        Given create backend oauth2 authorization with client id 'client_id'
    :
    :tag API Authorization Steps:
    :param context:
    :param client_id:
    :return:
    """
    if context.func.is_contains_profile_re_var(client_id):
        client_id = context.func.get_formatter_multiple_re_var(client_id, context.master_file_name_config)
    context.test_oauth2_auth = context.api.create_oauth2(flow="backend", client_id=client_id)
    data_dict = {
        "flow": "backend",
        "client_id": client_id
    }
    context.api.prepare_request(authorization=context.test_oauth2_auth)
    context.func.add_formatter_evidence_json(data_dict, "Prepared oauth2 authorization")


#######################################################################################################################
#                                               Response Steps                                                        #
#######################################################################################################################
@step(u"save response encoding")
def save_response_encoding(context):
    """
    This step saves in a context variable= context.test_response_encode
    :example
        Then save response encoding
    :
    :tag API Response Steps:
    :param context:
    :return context.test_response_encode:
    """
    encode = context.api.get_response_encoding()
    dict_evidence = {"Encoding": str(encode)}
    context.func.add_formatter_evidence_json(dict_evidence, "Response Encoding")
    context.test_response_encode = str(encode)


@step(u"create response image binary")
def create_response_image(context):
    """
    This step creates a binary image of the response
    The binary image will be saved in the context variable= context.test_response_image_binary
    :example
        Then create response image binary
    :
    :tag API Response Steps:
    :param context:
    :return context.test_response_image_binary:
    """
    context.test_response_image_binary = context.api.create_image_binary_response()


# @step(u"save response in the file with path '(?P<file_path>.+)'")
# def save_response_in_file_with_path(context, file_path):
#     """
#     This step saves the answer in a file whose path is passed by parameter
#     You can also use values with {{variable}} to reference a json / yaml key from the master file
#     :example
#         Then save response in the file with path 'files/response.txt'
#     :
#     :tag API Response Steps:
#     :param context:
#     :param file_path:
#     :return:
#     """
#     if context.func.is_contains_profile_re_var(file_path):
#         file_path = context.func.get_formatter_multiple_re_var(file_path, context.master_file_name_config)
#     context.api.save_response_into_file(file_path)


@step(u"add to the profile file '(?P<file_name>.+)' the response key value '(?P<r_key>.+)' with key '(?P<key>.+)'")
def add_value_to_profile_file(context, file_name, r_key, key):
    """
    Add to the profile file with a name passed by parameter a data with
    a named key passed by parameter the value of a response key
    the parameter "file_name" is the name of the profile file. The r_key parameter is the key of the value that we want
    to store in the profile file. And the "key" parameter is the name of the new (or existing key)
    where the response value will be stored in the profile file
    :example
           When add to the profile file 'calendars_datas' the response key value 'Authorization' with key 'Token_JWT'

    :
    :tag API Response Steps:
    :param context:
    :param file_name:
    :param r_key:
    :param key:
    :return:
    """
    response_dict = context.response.json()
    files.set_profile_data_value(file_name, key, response_dict[r_key], change_all_profiles=True)


#######################################################################################################################
#                                               Proxies Steps                                                         #
#######################################################################################################################
@step(u"configure the proxies with file path '(?P<file_path>.+)'")
def configure_proxies_with_file_path(context, file_path):
    """
    This step prepares the proxies using a file.
    You have to pass it the path of the file that contains the values of the proxies as a json / dictionary.
    The data dictionary of the json file passed by parameter will be saved
    in the context variable context.test_request_proxies
    The file_path parameter allows relative paths
    You can also use values with {{variable}} to reference a json / yaml key from the master file
    :example
        When configure the proxies with file path 'files/proxies.json'
    :
    :tag API Proxies Steps:
    :param context:
    :param file_path:
    :return context.test_request_headers:
    """
    if context.func.is_contains_profile_re_var(file_path):
        file_path = context.func.get_formatter_multiple_re_var(file_path, context.master_file_name_config)
    dict_proxies = dict(files.json_to_dict(file_path))
    context.api.prepare_request(proxies=dict_proxies)
    context.func.add_formatter_evidence_json(dict_proxies, "Prepared proxies")
    context.test_request_proxies = dict_proxies


@step(u"configure the proxies with key path '(?P<key_path>.+)' in file '(?P<file_name>.+)'")
def configure_proxies_with_key_path(context, key_path, file_name):
    """
    This step prepares the request proxies using a file and key path.
    You have to pass it the name of the profile file that contains the values of the proxies as a json / dictionary and
    and the path of keys to the values of the proxies:
    Where the separator character for the key paths will be the period "."
    Returning a dictionary with the values with the proxies of the json file
    The data dictionary of the json file passed by parameter will be saved in the
    context variable context.test_request_proxies
    :example
        When configure the proxies with key path 'proxy.santander_proxy' in file 'api_datas'
    :
    :tag API Proxies Steps:
    :param context:
    :param key_path:
    :param file_name:
    :return context.test_request_proxies:
    """
    dict_proxies = context.api.get_profile_value_key_path(key_path, file_name)
    context.api.prepare_request(proxies=dict_proxies)
    context.func.add_formatter_evidence_json(dict_proxies, "Prepared proxies")
    context.test_request_proxies = dict_proxies


@step(u"configure the proxies request")
def configure_headers_with_data_table(context):
    """
    This step prepares the proxies using data table of Gherkin.
    The data dictionary of the json file passed by parameter will be saved in the context
    variable context.test_request_proxies
    The data table supports two columns, one headed by key and the other by value.
    The data of the headers must be listed by protocol / url
    You can also use values with {{variable}} to reference a json / yaml key from the master file
    :example
        When prepare the proxies request
          | protocol   | url                     |
          | http       | 127.0.0.1:80            |
          | https      | https://corp.proxy:8080 |
          | ftp        | http://ftp.proxy:27     |
    :
    :tag API Proxies Steps:
    :param context:
    :return context.test_request_proxies:
    """
    dict_proxies = {}
    if context.table:
        for row in context.table:
            protocol = row["protocol"]
            url = row["url"]
            if context.func.is_contains_profile_re_var(protocol):
                protocol = context.func.get_formatter_multiple_re_var(protocol, context.master_file_name_config)
            if context.func.is_contains_profile_re_var(url):
                url = context.func.get_formatter_multiple_re_var(url, context.master_file_name_config)
            dict_proxies[protocol] = url
    context.api.prepare_request(proxies=dict_proxies)
    context.func.add_formatter_evidence_json(dict_proxies, "Prepared proxies")
    context.test_request_proxies = dict_proxies
