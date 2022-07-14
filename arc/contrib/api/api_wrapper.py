# TODO: refactorizar, optimizar y mejorar reporting
# TODO: añadir logger
import json
import os
import socket
from io import StringIO
from copy import deepcopy
from urllib.parse import urlparse
import jsonschema
import requests
from PIL import Image
from oauthlib.oauth2 import MobileApplicationClient, LegacyApplicationClient, BackendApplicationClient
from requests.auth import HTTPBasicAuth, HTTPDigestAuth
from requests.cookies import cookiejar_from_dict, RequestsCookieJar, create_cookie
from requests.utils import get_encodings_from_content, get_encoding_from_headers, get_unicode_from_response
from requests_oauthlib import OAuth1, OAuth2Session
from urllib3.connection import HTTPConnection

from arc.contrib.tools import files
from settings import settings

METHOD_GET = "GET"
METHOD_POST = "POST"
METHOD_PUT = "PUT"
METHOD_PATCH = "PATCH"
METHOD_DELETE = "DELETE"
METHOD_COPY = "COPY"
METHOD_HEAD = "HEAD"
METHOD_OPTIONS = "OPTIONS"
METHOD_LINK = "LINK"
METHOD_UNLINK = "UNLINK"
METHOD_PURGE = "PURGE"
METHOD_LOCK = "LOCK"
METHOD_UNLOCK = "UNLOCK"
METHOD_PROPFIND = "PROPFIND"
METHOD_VIEW = "VIEW"


class ApiObject:
    headers = None
    body = None
    method = None
    uri = None
    params = None
    authorization = None
    files = None
    ssl = False
    cookies = None
    data = None
    context = None
    response = None
    session = None
    prepare = None
    request = None
    proxies = None
    HTTPConnection.debuglevel = 0
    requests_log = None
    remote_ip = None

    def __init__(self, context):
        self.context = context

    def prepare_request(self, header=None, body=None, method=None, uri=None, params=None, authorization=None,
                        ssl=False, cookies=None, data=None, files=None, proxies=None):
        if header is not None: self.headers = header
        if body is not None: self.body = body
        if method is not None: self.method = method
        if uri is not None: self.uri = uri
        if files is not None: self.files = files
        if params is not None: self.params = params
        if authorization is not None: self.authorization = authorization
        if ssl is not None: self.ssl = ssl
        if cookies is not None: self.cookies = cookies
        if data is not None: self.data = data

        default_proxy = {}
        try:
            if settings.PYTALOS_RUN['execution_proxy']['enabled']:
                default_proxy['http'] = settings.PYTALOS_RUN['execution_proxy']['proxy']['http_proxy']
                default_proxy['https'] = settings.PYTALOS_RUN['execution_proxy']['proxy']['https_proxy']
                self.proxies = default_proxy
            else:
                self.proxies = default_proxy

        except(Exception,) as ex:
            print(ex)
            self.proxies = proxies

    def send_request(self):
        self.request = requests.Request(method=self.method, url=self.uri, headers=self.headers, json=self.body,
                                        params=self.params, auth=self.authorization, cookies=self.cookies,
                                        data=self.data, files=self.files)
        self.prepare = self.request.prepare()
        self.session = requests.Session()

        if self.proxies is not None: self.session.proxies.update(self.proxies)

        self.response = self.session.send(self.prepare, verify=self.ssl)

        if self.response is None:
            raise Exception(
                'The response is None\n'
                'ERROR: Check that the call was made correctly, this error usually occurs when the uri is badly formed')

        else:
            self.context.api.response = self.response
            try:
                self.context.api.json_response = self.response.json()
            except json.decoder.JSONDecodeError as ex:
                try:
                    self.context.api.json_response = self.response.text
                except (Exception,):
                    raise Exception('ERROR: verifies that the response returns a JSON type body')

        datas_dict = {
            "URL": self.uri,
            "Method": self.method,
            "response": self.response,
            "headers": self.headers,
            "body": self.body,
        }

        self.generate_evidence(datas_dict)
        return self.response

    def create_basic_authorization(self, username, password, auth_type="basic"):
        if auth_type.lower() == "basic":
            auth = HTTPBasicAuth(username, password)
        elif auth_type.lower() == "digest":
            auth = HTTPDigestAuth(username, password)
        else:
            raise Exception("auth_type does not exist: try basic or digest")

        self.context.api.api_auth = auth
        return auth

    def create_oauth1(self, app_key, app_secret, user_oauth_token, user_oauth_token_secret):
        auth = OAuth1(app_key, app_secret, user_oauth_token, user_oauth_token_secret)
        self.context.api.auth = auth
        return auth

    def create_oauth2(self, flow=None, client_id=None, client_secret=None, url=None, scope=None):
        if flow == "web" and client_id and client_secret and url and scope:
            oauth = OAuth2Session(client_id, redirect_uri=url, scope=scope)
        elif flow == "mobile" and client_id and url and scope:
            oauth = OAuth2Session(client=MobileApplicationClient(client_id=client_id), scope=scope)
        elif flow == "legacy" and client_id:
            oauth = OAuth2Session(client=LegacyApplicationClient(client_id=client_id))
        elif flow == "backend" and client_id:
            client = BackendApplicationClient(client_id=client_id)
            oauth = OAuth2Session(client=client)
        else:
            raise Exception(
                "the flow parameter must be filled with some of the following values: web, mobile, legacy or"
                "backend")

        self.context.api.auth = oauth
        return oauth

    @staticmethod
    def formatter_table_to_dict(table, key="key", value="value"):
        params = {}
        if table:
            for row in table:
                params[row[key]] = row[value]
        return params

    @staticmethod
    def decompose_url(url):
        parsed = urlparse(url)
        url_protocol = parsed.scheme
        url_hostname = parsed.hostname
        url_path = []
        url_query = {}
        if parsed.path:
            path = parsed.path.split('/')
            path.pop(0)
            url_path = path
        if parsed.query:
            query = parsed.query.split('&')
            for p in query:
                d = p.split('=')
                url_query[d[0]] = d[1]
        return [url_protocol, url_hostname, url_path, url_query]

    @staticmethod
    def compose_url_with_params(url, dict_params: dict):
        url += "?"
        len_dict = len(dict_params)
        cont = 1
        for param in dict_params:
            if cont == len_dict:
                url += param.key + "=" + param.value
            else:
                url += param.key + "=" + param.value + "&"
            cont += 1
        return url

    @staticmethod
    def response_to_json(response):
        return response.json()

    def send_simple_request(self, uri, method: str, params=None, headers: dict = None, data: dict = None,
                            allow_redirects: bool = None, timeout=None, files=None):

        self.headers = headers
        self.body = data
        self.method = method
        self.uri = uri
        self.params = params

        if data is None:
            data = {}

        if method.lower() == "post":
            response = requests.post(uri, params=params, headers=headers, data=json.dumps(data),
                                     allow_redirects=allow_redirects, timeout=timeout, files=files)
        elif method.lower() == "get":
            response = requests.get(uri, params=params, headers=headers, data=json.dumps(data),
                                    allow_redirects=allow_redirects, timeout=timeout)
        elif method.lower() == "put":
            response = requests.put(uri, params=params, headers=headers, data=json.dumps(data),
                                    allow_redirects=allow_redirects, timeout=timeout)
        elif method.lower() == "delete":
            response = requests.delete(uri, params=params, headers=headers, data=json.dumps(data),
                                       allow_redirects=allow_redirects, timeout=timeout)
        elif method.lower() == "head":
            response = requests.head(uri, params=params, headers=headers, data=json.dumps(data),
                                     allow_redirects=allow_redirects, timeout=timeout)
        elif method.lower() == "options":
            response = requests.options(uri, params=params, headers=headers, data=json.dumps(data),
                                        allow_redirects=allow_redirects, timeout=timeout)
        else:
            raise Exception("Method not implemented or does not exist")

        self.response = response

        datas_dict = {
            "URL": self.uri,
            "Method": self.method,
            "response": self.response,
            "headers": self.headers,
            "body": self.body,
        }
        self.generate_evidence(datas_dict)

        return response

    def get_response_text(self):
        return self.response.text

    def get_response_encoding(self):
        return self.response.encoding

    def get_response_binary(self):
        return self.response.content

    def create_image_binary_response(self):
        return Image.open(StringIO(self.response.content))

    def get_response_json(self):
        return self.response.json()

    def get_response_raw(self):
        return self.response.raw

    def get_remote_ip(self):
        try:
            url = self.decompose_url(self.uri)
            if str(url).startswith("www."):
                self.remote_ip = socket.gethostbyname(url[1])
            else:
                self.remote_ip = socket.gethostbyname("www." + url[1])
            return self.remote_ip
        except socket.error:
            return "Unknown or unreachable"

    def save_response_into_file(self, file_path, chuck_size=8192):
        with open(file_path, 'wd') as fd:
            for chunk in self.response.iter_content(chunk_size=chuck_size):
                fd.write(chunk)

    def get_response_history(self):
        return self.response.history

    def get_response_headers(self):
        return self.response.headers

    @staticmethod
    def get_encodings_from_content(content):
        return get_encodings_from_content(content)

    @staticmethod
    def get_encoding_from_headers(headers):
        return get_encoding_from_headers(headers)

    def get_unicode_from_response(self):
        return get_unicode_from_response(self.response)

    @staticmethod
    def dict_from_cookiejar(cookie_jar):
        cookie_dict = {}
        for cookie in cookie_jar:
            cookie_dict[cookie.name] = cookie.value

        return cookie_dict

    @staticmethod
    def add_dict_to_cookiejar(cookie_jar, cookie_dict):
        return cookiejar_from_dict(cookie_dict, cookie_jar)

    @staticmethod
    def cookiejar_from_dict(cookie_dict, cookiejar=None, overwrite=True):
        if cookiejar is None:
            cookiejar = RequestsCookieJar()

        if cookie_dict is not None:
            names_from_jar = [cookie.name for cookie in cookiejar]
            for name in cookie_dict:
                if overwrite or (name not in names_from_jar):
                    cookiejar.set_cookie(create_cookie(name, cookie_dict[name]))

        return cookiejar

    def get_log(self):
        return self.requests_log

    """
    Verifications
    """

    def verify_simple_value_in_response(self, key, value_expected, response=None):
        if response is None:
            response = self.response
        json_response = self.response_to_json(response)

        error_message = None
        exception = ""

        try:
            assert str(key) in json_response
            result_flag = "Passed"
        except Exception as ex:
            result_flag = "Failed"
            exception = str(ex)
            error_message = "The " + key + " key is not in the response json"
        self._generate_dict_evidence("Verify key in Json response", key=str(key),
                                     value_expected=None, current_value=None,
                                     result_flag=result_flag, error_message=error_message)
        try:
            assert value_expected == json_response[key]
            current_value = str(json_response[key])
            result_flag = "Passed"
        except KeyError as ex:
            result_flag = "Failed"
            current_value = "KeyError"
            exception = str(ex) + " is not a correct key"
            error_message = "Unable to check current value because key is not correct"
        except Exception as ex:
            result_flag = "Failed"
            current_value = str(json_response[key])
            exception = str(ex)
            error_message = "The expected value " + str(
                value_expected) + " is not equal or is not of the same data type as the current value " \
                            + current_value + " with type " + str(type(current_value)) + "of the response json"
        self._generate_dict_evidence("Verify value expected is equal current value", key=str(key),
                                     value_expected=value_expected, current_value=current_value,
                                     result_flag=result_flag, error_message=error_message)
        if result_flag != "Passed":
            raise Exception(exception)

    def verify_value_in_response_with_path(self, param_path_key: str, value_expected, response=None,
                                           sep_char: str = "."):
        if response is None:
            response = self.response

        params_list = param_path_key.split(sep_char)
        aux_json = deepcopy(self.response_to_json(response))
        error_message = None
        current_value = None
        exception = ""

        try:
            for param in params_list:
                if type(aux_json) is list:
                    aux_json = aux_json[int(param)]
                else:
                    aux_json = aux_json[param]
            result_flag = "Passed"
            current_value = os.path.expandvars(aux_json) if aux_json and type(aux_json) not in [int, bool,
                                                                                                float] else aux_json
            assert current_value == value_expected

        except KeyError as ex:
            current_value = None
            exception = str(ex) + " is not a correct key"
            result_flag = "Failed"
            error_message = "{param_value} not found in the file or json structure".format(param_value=param_path_key)
        except ValueError as ex:
            current_value = None
            exception = str(ex)
            result_flag = "Failed"
            error_message = "This value {param_value} is not valid".format(param_value=param_path_key)
        except IndexError as ex:
            current_value = None
            exception = str(ex)
            result_flag = "Failed"
            error_message = "Index {param_value} not found in the file or json structure".format(
                param_value=param_path_key)
        except Exception as ex:
            exception = str(ex)
            result_flag = "Failed"
            error_message = "The expected value " + str(value_expected) + " is not equal or is not of the same data " \
                                                                          "type as the current value " + current_value \
                            + " with type " + str(
                type(current_value)) + "of the response json"
        self._generate_dict_evidence("Verify value expected in response Json", key=str(param_path_key),
                                     value_expected=value_expected, current_value=current_value,
                                     result_flag=result_flag, error_message=error_message)
        if result_flag != "Passed":
            raise Exception(exception)

    def validate_json_schema(self, expected_schema, json_response=None, input_type="json"):
        if json_response is None:
            json_response = self.response.json()

        error_message = None
        exception = ""

        try:
            if input_type.lower() == "json" and json_response:
                jsonschema.validate(instance=json_response, schema=expected_schema)
            elif (input_type.lower() == "str" or input_type.lower() == "dict") and json_response:
                json_schema = json.loads(expected_schema)
                json_response_v = json.loads(json_response)
                jsonschema.validate(instance=json_response_v, schema=json_schema)
            elif input_type.lower() == "json_file" and json_response:
                json_schema = files.json_to_dict(expected_schema)
                json_response_v = files.json_to_dict(json_response)
                jsonschema.validate(instance=json_response_v, schema=json_schema)
            elif input_type.lower() == "json" and json_response is None:
                jsonschema.validate(instance=self.response.json(), schema=expected_schema)
            elif (input_type.lower() == "str" or input_type.lower() == "dict") and json_response is None:
                json_schema = json.loads(expected_schema)
                jsonschema.validate(instance=self.response.json(), schema=json_schema)
            elif input_type.lower() == "json_file" and json_response is None:
                json_schema = files.json_to_dict(expected_schema)
                jsonschema.validate(instance=self.response.json(), schema=str(json_schema))

            result_flag = "Passed"

        except Exception as ex:
            exception = str(ex)
            result_flag = "Failed"
            error_message = "The schema does not match the response json"

        self._generate_dict_evidence("Verify json schema", key=None, value_expected=None, current_value=None,
                                     schema_type=input_type,
                                     result_flag=result_flag, error_message=error_message)

        self.context.func.add_formatter_evidence_json(expected_schema, "Schema")

        if result_flag != "Passed":
            raise Exception(exception)

    def verify_status_code(self, expect_status_code, response=None):
        if response is None:
            response = self.response

        current_value = response.status_code
        exception = None
        try:
            assert response.status_code == expect_status_code
            result_flag = "Passed"
            error_message = None
        except Exception as ex:
            exception = str(ex)
            result_flag = "Failed"
            error_message = "The expected status code " + str(
                expect_status_code) + " is not equal to the current value " + str(current_value)

        self._generate_dict_evidence("Verify status code", key=None,
                                     value_expected=expect_status_code, current_value=current_value,
                                     result_flag=result_flag, error_message=error_message)

        if result_flag != "Passed":
            raise Exception(exception)

    def verify_response_contains_value(self, value, response):
        if response is None:
            response = self.response
        exception = None
        try:
            assert value in response.text
            result_flag = "Passed"
            error_message = None
        except Exception as ex:
            exception = str(ex)
            result_flag = "Failed"
            error_message = "The expected value " + str(value) + " is not in the response"
        self._generate_dict_evidence("Verify status code", key=None,
                                     value_expected=value, current_value=None,
                                     result_flag=result_flag, error_message=error_message)

        if result_flag != "Passed":
            raise Exception(exception)

    def verify_response_headers_contains_value(self, value, response=None):
        if response is None:
            response = self.response
        exception = None
        result_flag = "Failed"
        error_message = None
        try:
            current_value = None
            for key in response.headers.keys():
                if value in response.headers[key]:
                    result_flag = "Passed"
                    current_value = response.headers[key]
                    break
                else:
                    current_value = None
                    result_flag = "Failed"

            assert current_value in value

        except Exception as ex:
            exception = str(ex)
            result_flag = "Failed"
            error_message = "The expected value " + str(value) + " is not in the response header"
        self._generate_dict_evidence("Verify response headers", key=None,
                                     value_expected=value, current_value=None,
                                     result_flag=result_flag, error_message=error_message)
        self.context.api_evidence_auto_extra_json.append(self.formatter_evidence_json(dict(response.headers)))

        if result_flag != "Passed":
            raise Exception(exception)

    def verify_values(self, value_expected, current_value):
        exception = None
        try:
            assert value_expected == current_value
            result_flag = "Passed"
            error_message = None
        except Exception as ex:
            exception = str(ex)
            result_flag = "Failed"
            error_message = "The expected value " + str(
                value_expected) + " is not equal to the current value " + str(current_value)

        self._generate_dict_evidence("Verify values", key=None,
                                     value_expected=value_expected, current_value=current_value,
                                     result_flag=result_flag, error_message=error_message)

        if result_flag != "Passed":
            raise Exception(exception)

    def verify_response_reason(self, expected_reason, response=None):
        if response is None:
            response = self.response

        current_value = response.reason
        exception = None
        try:
            assert self.response.reason == expected_reason
            result_flag = "Passed"
            error_message = None
        except Exception as ex:
            exception = str(ex)
            result_flag = "Failed"
            error_message = "The expected status code " + str(
                expected_reason) + " is not equal to the current value " + str(current_value)

        self._generate_dict_evidence("Verify status code", key=None,
                                     value_expected=expected_reason, current_value=current_value,
                                     result_flag=result_flag, error_message=error_message)

        if result_flag != "Passed":
            raise Exception(exception)

    def verify_response_value_type(self, key, expected_type, response=None):
        if response is None:
            response = self.response
        json_response = self.response_to_json(response)
        current_value = None
        exception = ""
        try:
            current_value = type(json_response[key])
            assert type(json_response[key]) is expected_type
            result_flag = "Passed"
            error_message = None
        except KeyError as ex:
            result_flag = "Failed"
            current_value = "KeyError"
            exception = str(ex) + " is not a correct key"
            error_message = "Unable to check current value because key is not correct"
        except Exception as ex:
            result_flag = "Failed"
            exception = str(ex)
            error_message = "The data type of the " + key + " key is not equal to the current data type"

        self._generate_dict_evidence("Verify data type", key=key,
                                     value_expected=str(expected_type), current_value=str(current_value),
                                     result_flag=result_flag, error_message=error_message)

        if result_flag != "Passed":
            raise Exception(exception)

    def verify_response_contains_key(self, key, response=None):
        if response is None:
            response = self.response
        exception = None
        error_message = None
        keys = []
        json_dict = {}

        try:
            try:
                for key_d in response.json().keys():
                    if key_d not in keys:
                        keys.append(key_d)
                        json_dict.setdefault("response_keys", []).append(key_d)

            except Exception as ex:
                response_json = response.json()
                for json_values in response_json:
                    for key_l in json_values.keys():
                        if key_l not in keys:
                            keys.append(key_l)
                            json_dict.setdefault("response_keys", []).append(key_l)

            assert key in keys
            result_flag = "Passed"
        except Exception as ex:
            exception = str(ex)
            result_flag = "Failed"
            error_message = "The expected value " + str(key) + " is not in the response keys"
        self._generate_dict_evidence("Verify response keys", key=None,
                                     value_expected=key, current_value=None,
                                     result_flag=result_flag, error_message=error_message)

        self.context.func.add_formatter_evidence_json(json_dict, "Verify response keys")
        if result_flag != "Passed":
            raise Exception(exception)

    def verify_value_type_in_response_with_path(self, param_path_key: str, value_expected, response=None,
                                                sep_char: str = "."):
        if response is None:
            response = self.response
        params_list = param_path_key.split(sep_char)
        aux_json = deepcopy(self.response_to_json(response))

        error_message = None
        current_value = None
        exception = ""

        try:
            for param in params_list:
                if type(aux_json) is list:
                    aux_json = aux_json[int(param)]
                else:
                    aux_json = aux_json[param]
            result_flag = "Passed"
            current_value = os.path.expandvars(aux_json) if aux_json and type(aux_json) not in [int, bool,
                                                                                                float] else aux_json
            assert type(current_value) is value_expected
        except KeyError as ex:
            current_value = None
            exception = str(ex) + " is not a correct key"
            result_flag = "Failed"
            error_message = "{param_value} not found in the file or json structure".format(param_value=param_path_key)
        except ValueError as ex:
            current_value = None
            exception = str(ex)
            result_flag = "Failed"
            error_message = "This value {param_value} is not valid".format(param_value=param_path_key)
        except IndexError as ex:
            current_value = None
            exception = str(ex)
            result_flag = "Failed"
            error_message = "Index {param_value} not found in the file or json structure".format(
                param_value=param_path_key)
        except Exception as ex:
            exception = str(ex)
            result_flag = "Failed"
            error_message = "The expected value type " + str(
                type(value_expected)) + " is not equal type as the current value " + str(current_value)
        self._generate_dict_evidence("Verify type expected in response Json", key=str(param_path_key),
                                     value_expected=str(value_expected), current_value=str(type(current_value)),
                                     result_flag=result_flag, error_message=error_message)
        if result_flag != "Passed":
            raise Exception(exception)

    def response_time_is_less_than(self, seconds_expected, response=None):
        if response is None:
            response = self.response

        exception = None
        current_value = response.elapsed.total_seconds()
        try:
            assert current_value < seconds_expected
            result_flag = "Passed"
            error_message = None

        except Exception as ex:
            exception = str(ex)
            result_flag = "Failed"
            error_message = "The time expected of the response " + str(
                seconds_expected) + " seconds is greater than the time executed " + str(current_value) + " seconds"

        self._generate_dict_evidence("Verify response time is less than " + str(seconds_expected) + " seconds",
                                     key=None, schema_type=None,
                                     value_expected=str(seconds_expected) + " seconds",
                                     current_value=str(current_value) + " seconds",
                                     result_flag=result_flag, error_message=error_message)

        if result_flag != "Passed":
            raise Exception(exception)

    def response_time_is_greater_than(self, seconds_expected, response=None):
        if response is None:
            response = self.response

        exception = None
        current_value = response.elapsed.total_seconds()
        try:
            assert current_value > seconds_expected
            result_flag = "Passed"
            error_message = None

        except Exception as ex:
            exception = str(ex)
            result_flag = "Failed"
            error_message = "The time expected of the response " + str(
                seconds_expected) + " seconds is less than the time executed " + str(current_value) + " seconds"

        self._generate_dict_evidence("Verify response time is greater than " + str(seconds_expected) + " seconds",
                                     key=None, schema_type=None,
                                     value_expected=str(seconds_expected) + " seconds",
                                     current_value=str(current_value) + " seconds",
                                     result_flag=result_flag, error_message=error_message)

        if result_flag != "Passed":
            raise Exception(exception)

    def response_time_is_between(self, less_expected, greater_expected, response=None):
        if response is None:
            response = self.response

        exception = None
        current_value = response.elapsed.total_seconds()
        try:
            assert less_expected < current_value
            assert current_value < greater_expected

            result_flag = "Passed"
            error_message = None

        except Exception as ex:
            exception = str(ex)
            result_flag = "Failed"
            error_message = "The current response time is not between the values​ " + str(less_expected) + " and " \
                            + str(greater_expected) + " seconds"

        self._generate_dict_evidence(
            "Verify response time is between " + str(less_expected) + " and " + str(greater_expected) + " seconds",
            key=None, schema_type=None,
            value_expected=str(less_expected) + " - " + str(greater_expected) + " seconds",
            current_value=str(current_value) + " seconds",
            result_flag=result_flag, error_message=error_message)

        if result_flag != "Passed":
            raise Exception(exception)

    def status_code_is_one_of(self, expected_values: list, response=None):
        if response is None:
            response = self.response

        current_value = response.status_code
        exception = None
        try:
            assert current_value in expected_values
            result_flag = "Passed"
            error_message = None

        except Exception as ex:
            exception = str(ex)
            result_flag = "Failed"
            error_message = "The expected status codes " + str(
                expected_values) + " are not equal to the current status code " + str(current_value)

        self._generate_dict_evidence("Verify status code is one of the list", key=None,
                                     value_expected=str(expected_values), current_value=current_value,
                                     result_flag=result_flag, error_message=error_message)

        if result_flag != "Passed":
            raise Exception(exception)

    @staticmethod
    def formatter_evidence_json(data):
        return json.dumps(data, sort_keys=True, indent=4)

    def generate_evidence(self, arguments):
        self.context.api_evidence_info = {"URL": arguments["URL"], "Method": arguments["Method"],
                                          "Reason": str(arguments["response"].reason),
                                          "Status Code": str(arguments["response"].status_code),
                                          "Remote Address": self.get_remote_ip()}
        self.context.api_evidence_request_headers = arguments["headers"]
        self.context.api_evidence_request_body.append(arguments["body"])
        try:
            self.context.api_evidence_response = self.formatter_evidence_json(arguments["response"].json())
        except json.decoder.JSONDecodeError:
            try:
                self.context.api_evidence_response = arguments["response"].text
            except(Exception,):
                self.context.api_evidence_response = ""

    def generate_verify_evidence(self, info):
        self.context.api_evidence_verify.append(info)

    def _generate_dict_evidence(self, name, key=None, value_expected=None, current_value=None, result_flag=None,
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
        dictionary["Assert Result"] = result_flag
        dictionary["Error Message"] = error_message
        self.generate_verify_evidence(dictionary)

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

    def get_request_url(self):
        return self.response.url

    def get_response_value_key_path(self, param_path_key, sep_char: str = "."):
        params_list = param_path_key.split(sep_char)
        response_datas = self.response.json()
        aux_json = deepcopy(response_datas)
        for param in params_list:
            if type(aux_json) is list:
                aux_json = aux_json[int(param)]
            else:
                aux_json = aux_json[param]
        return aux_json
