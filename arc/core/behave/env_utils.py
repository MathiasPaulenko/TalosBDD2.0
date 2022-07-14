# -*- coding: utf-8 -*-
import configparser
import datetime
import json
import logging
import os
import traceback
import warnings
import sys

from faker import Faker
from pkg_resources import parse_version

from arc.reports.html.element import Element
from arc.reports.html.feature import Feature
from arc.reports.html.htmlGenerator import HtmlGenerator
from arc.reports.html.utils import BASE_DIR
from settings import settings
from arc.contrib.host import host
from arc.contrib.host.utils import get_host_screenshot
from arc.core import constants
from arc.core.config_manager import ConfigFiles
from arc.core.behave.context_utils import PyTalosContext
from arc.core.driver.driver_manager import DriverManager
from arc.integrations import jira
from arc.page_elements import PageElement
from arc.core.test_method.visual_test import VisualTest
from arc.reports import log_generation, html_reporter
from arc.reports import generate_json
from arc.reports.doc import generate_doc
from test.helpers import hooks

warnings.filterwarnings('ignore')


class Logger:
    def __init__(self, logger, show):
        self.logger = logger
        self.show = show

    def warn(self, exc):
        msg = 'trying to execute a step in the environment: \n' \
              f"           - Exception: {exc}"
        if self.logger is not None:
            self.logger.warn(msg)
        self.by_console(f"      WARN - {msg}")

    def error(self, exc):
        msg = 'trying to execute a step in the environment: \n' \
              f"           - Exception: {exc}"
        if self.logger is not None:
            self.logger.error(msg)
        self.by_console(f"      ERROR - {msg}")

    def debug(self, value):
        if self.logger is not None:
            self.logger.debug(value)

    def by_console(self, text_to_print):
        if self.show:
            sys.stdout.write(f"{text_to_print}\n")
            sys.stdout.flush()


class DynamicEnvironment:
    actions = None

    def __init__(self, **kwargs):
        logger_class = kwargs.get("logger", None)
        self.show = kwargs.get("show", True)
        self.logger = Logger(logger_class, self.show)
        self.init_actions()
        self.scenario_counter = 0
        self.feature_error = False
        self.scenario_error = False

    def init_actions(self):
        self.actions = {
            constants.ACTIONS_BEFORE_FEATURE: [],
            constants.ACTIONS_BEFORE_SCENARIO: [],
            constants.ACTIONS_AFTER_SCENARIO: [],
            constants.ACTIONS_AFTER_FEATURE: []
        }

    def get_steps_from_feature_description(self, description):
        self.init_actions()
        label = constants.EMPTY
        for row in description:
            if label != constants.EMPTY:
                if "#" in row:
                    row = row[0:row.find("#")].strip()

                if any(row.startswith(x) for x in constants.KEYWORDS):
                    self.actions[label].append(row)
                elif row.find(constants.TABLE_SEPARATOR) >= 0:
                    self.actions[label][-1] = "%s\n      %s" % (self.actions[label][-1], row)
                else:
                    label = constants.EMPTY
            for action_label in self.actions:
                if row.lower().find(action_label) >= 0:
                    label = action_label

    @staticmethod
    def __remove_prefix(step):
        step_length = len(step)
        for k in constants.KEYWORDS:
            step = step.lstrip(k)
            if len(step) < step_length:
                break
        return step

    def __print_step(self, step):
        step_list = step.split(u'\n')
        for s in step_list:
            self.logger.by_console(u'    %s' % repr(s).replace("u'", "").replace("'", ""))

    def __execute_steps_by_action(self, context, action):
        if len(self.actions[action]) > 0:
            if action in [constants.ACTIONS_BEFORE_FEATURE, constants.ACTIONS_BEFORE_SCENARIO,
                          constants.ACTIONS_AFTER_FEATURE]:
                self.logger.by_console('\n')
                if action == constants.ACTIONS_BEFORE_SCENARIO:
                    self.scenario_counter += 1
                    self.logger.by_console(
                        f"  ------------------ Scenario Number: {self.scenario_counter} ------------------")
                self.logger.by_console('  %s:' % action)
            for item in self.actions[action]:
                self.scenario_error = False
                try:
                    self.__print_step(item)
                    context.execute_steps(u'''%s%s''' % (constants.GIVEN_PREFIX, self.__remove_prefix(item)))
                    self.logger.debug(u'step defined in pre-actions: %s' % repr(item))
                except Exception as exc:
                    if action in [constants.ACTIONS_BEFORE_FEATURE]:
                        self.feature_error = True
                    elif action in [constants.ACTIONS_BEFORE_SCENARIO]:
                        self.scenario_error = True
                    self.logger.error(exc)
                    self.error_exception = exc
                    break

    def reset_error_status(self):
        try:
            return self.feature_error or self.scenario_error
        finally:
            self.feature_error = False
            self.scenario_error = False

    def execute_before_feature_steps(self, context):
        self.__execute_steps_by_action(context, constants.ACTIONS_BEFORE_FEATURE)

        if context.pytalos.dyn_env.feature_error:
            context.feature.mark_skipped()

    def execute_before_scenario_steps(self, context):
        if not self.feature_error:
            self.__execute_steps_by_action(context, constants.ACTIONS_BEFORE_SCENARIO)

        if context.pytalos.dyn_env.scenario_error:
            context.scenario.mark_skipped()

    def execute_after_scenario_steps(self, context):
        if not self.feature_error and not self.scenario_error:
            self.__execute_steps_by_action(context, constants.ACTIONS_AFTER_SCENARIO)

        if self.reset_error_status():
            context.scenario.reset()
            context.pytalos.dyn_env.fail_first_step_precondition_exception(context.scenario)

    def execute_after_feature_steps(self, context):
        if not self.feature_error:
            self.__execute_steps_by_action(context, constants.ACTIONS_AFTER_FEATURE)

        if self.reset_error_status():
            context.feature.reset()
            for scenario in context.feature.walk_scenarios():
                context.pytalos.dyn_env.fail_first_step_precondition_exception(scenario)

    def fail_first_step_precondition_exception(self, scenario):
        try:
            import behave
            if parse_version(behave.__version__) < parse_version('1.2.6'):
                status = 'failed'
            else:
                status = behave.model_core.Status.failed
        except ImportError as exc:
            self.logger.error(exc)
            raise

        scenario.steps[0].status = status
        scenario.steps[0].exception = Exception("Preconditions failed")
        scenario.steps[0].error_message = self.error_exception.message


def configure_properties_from_tags(context, scenario):
    if 'no_reset_app' in scenario.tags:
        os.environ["AppiumCapabilities_noReset"] = 'true'
        os.environ["AppiumCapabilities_fullReset"] = 'false'
    elif 'reset_app' in scenario.tags:
        os.environ["AppiumCapabilities_noReset"] = 'false'
        os.environ["AppiumCapabilities_fullReset"] = 'false'
    elif 'full_reset_app' in scenario.tags:
        os.environ["AppiumCapabilities_noReset"] = 'false'
        os.environ["AppiumCapabilities_fullReset"] = 'true'

    if 'reset_driver' in scenario.tags:
        DriverManager.stop_drivers()
        DriverManager.download_videos('multiple tests', context.pytalos.global_status['test_passed'])
        DriverManager.save_all_ggr_logs('multiple tests', context.pytalos.global_status['test_passed'])
        DriverManager.remove_drivers()
        context.pytalos.global_status['test_passed'] = True

    if 'android_only' in scenario.tags and context.pytalos.driver_wrapper.is_ios_test():
        scenario.skip('Android scenario')
        return
    elif 'ios_only' in scenario.tags and context.pytalos.driver_wrapper.is_android_test():
        scenario.skip('iOS scenario')
        return


def utils_before_all(context):
    env = context.config.userdata.get('Config_environment')
    context.pytalos = PyTalosContext(context)

    if env:
        os.environ['Config_environment'] = env

    if not hasattr(context, 'config_files'):
        context.pytalos.config_files = ConfigFiles()
    context.pytalos.config_files = DriverManager.initialize_config_files(context.pytalos.config_files)

    if not context.pytalos.config_files.config_directory:
        context.pytalos.config_files.set_config_directory(DriverManager.get_default_config_directory())

    context.pytalos.global_status = {'test_passed': True}
    create_wrapper(context)

    context.pytalos.dyn_env = DynamicEnvironment(logger=context.logger)


def utils_before_feature(context, feature):
    context.pytalos.global_status = {'test_passed': True}

    no_driver = 'no_driver' in feature.tags

    context.pytalos.reuse_driver_from_tags = 'reuse_driver' in feature.tags
    if context.pytalos_config.getboolean_optional('Driver', 'reuse_driver') or context.pytalos.reuse_driver_from_tags:
        start_driver(context, no_driver)

    context.pytalos.dyn_env.get_steps_from_feature_description(feature.description)
    context.pytalos.dyn_env.execute_before_feature_steps(context)


def utils_before_scenario(context, scenario):
    configure_properties_from_tags(context, scenario)
    no_driver = 'no_driver' in scenario.tags or 'no_driver' in scenario.feature.tags
    start_driver(context, no_driver)
    add_assert_screenshot_methods(context, scenario)
    context.logger.info(f"Running new scenario: {scenario.name}")
    context.pytalos.dyn_env.execute_before_scenario_steps(context)


def utils_after_scenario(context, scenario, status):
    if status == 'skipped':
        return
    elif status == 'passed':
        context.logger.info(f"The scenario {scenario.name} has passed")
    else:
        context.logger.error(f"The scenario {scenario.name} has failed")
        context.pytalos.global_status['test_passed'] = False

    DriverManager.close_drivers(
        scope='function',
        test_name=scenario.name,
        test_passed=status == 'passed',
        context=context
    )


def utils_after_feature(context, feature):
    context.pytalos.dyn_env.execute_after_feature_steps(context)

    DriverManager.close_drivers(
        scope='module',
        test_name=feature.name,
        test_passed=context.pytalos.global_status['test_passed']
    )


def utils_after_all(context):
    DriverManager.close_drivers(
        scope='session',
        test_name='multiple_tests',
        test_passed=context.pytalos.global_status['test_passed']
    )


def create_wrapper(context):
    context.pytalos.driver_wrapper = DriverManager.get_default_wrapper()
    context.utils = context.pytalos.driver_wrapper.utils

    try:
        behave_properties = context.config.userdata
    except AttributeError:
        behave_properties = None

    context.pytalos.driver_wrapper.configure(context.pytalos.config_files, behave_properties=behave_properties)
    context.pytalos_config = context.pytalos.driver_wrapper.config
    context.logger = logging.getLogger(__name__)


def connect_wrapper(context):
    if context.pytalos.driver_wrapper.driver:
        context.driver = context.pytalos.driver_wrapper.driver
    else:
        context.driver = context.pytalos.driver_wrapper.connect()

    context.pytalos.app_strings = context.pytalos.driver_wrapper.app_strings


def start_driver(context, no_driver):
    create_wrapper(context)
    if not no_driver:
        connect_wrapper(context)


def add_assert_screenshot_methods(context, scenario):
    file_suffix = scenario.name

    def assert_screenshot(element_or_selector, filename, threshold=0, exclude_elements=None, driver_wrapper=None,
                          force=False):
        if exclude_elements is None:
            exclude_elements = []
        VisualTest(driver_wrapper, force).assert_screenshot(element_or_selector,
                                                            filename,
                                                            file_suffix,
                                                            threshold,
                                                            exclude_elements)

    def assert_full_screenshot(filename, threshold=0, exclude_elements=None, driver_wrapper=None, force=False):
        if exclude_elements is None:
            exclude_elements = []
        VisualTest(driver_wrapper, force).assert_screenshot(None,
                                                            filename,
                                                            file_suffix,
                                                            threshold,
                                                            exclude_elements)

    def assert_screenshot_page_element(self, filename, threshold=0, exclude_elements=None, force=False):
        if exclude_elements is None:
            exclude_elements = []
        VisualTest(self.driver_wrapper, force).assert_screenshot(self.web_element,
                                                                 filename,
                                                                 file_suffix,
                                                                 threshold,
                                                                 exclude_elements)

    context.assert_screenshot = assert_screenshot
    context.assert_full_screenshot = assert_full_screenshot
    PageElement.assert_screenshot = assert_screenshot_page_element


def set_reporting_config_path(context):
    config_home = 'arc/settings' + os.sep
    context.reporting_config = configparser.ConfigParser()
    context.reporting_config.read_file(open(config_home + 'reporting.conf', encoding='utf8'))


def enable_jira_report():
    if settings.PYTALOS_JIRA['post_to_jira']:
        return jira.Jira()


def enable_txt_report():
    if settings.PYTALOS_REPORTS['generate_txt']:
        return log_generation.ExecutionTxtLog()


def enable_doc_report(scenario):
    if settings.PYTALOS_REPORTS['generate_docx']:
        return generate_doc.GenerateDoc(scenario)


def set_doc_info_and_end(context, scenario):
    if settings.PYTALOS_REPORTS['generate_docx']:
        try:
            context.runtime.doc.set_init_info(scenario)
            return context.runtime.doc.end(context)
        except (Exception,):
            return ''


def set_doc_note(generate, context):
    if generate:
        try:
            context.runtime.doc.add_note = ''
        except (Exception,):
            pass


def set_alm_custom_variable(context):
    context.runtime.step.result_expected = None
    context.runtime.step.obtained_result_failed = None
    context.runtime.step.obtained_result_passed = None
    context.runtime.step.obtained_result_skipped = None


def enable_json_report(scenario):
    if settings.PYTALOS_ALM['generate_json']:
        return generate_json.GenerateJson(scenario)


def enable_host(context):
    if context.pytalos_config.get('Driver', 'type') == 'host':
        ws_path = context.pytalos_config.get('Driver', 'ws_path')
        cscript = context.pytalos_config.get('Driver', 'cscript_path')
        context.host = host.Host(ws_path, cscript)


def close_host(context):
    if context.pytalos_config.get('Driver', 'type') == 'host':
        if settings.PYTALOS_RUN['close_host']:
            context.host.close_emulator()


def config_faker():
    return Faker(settings.PYTALOS_PROFILES['locale_fake_data'])


def run_hooks(context, moment, extra_info=None):
    try:
        if moment == 'before_all':
            hooks.before_all(context)
        elif moment == 'after_all':
            hooks.after_all(context)
        elif moment == 'before_feature':
            hooks.before_feature(context, extra_info)
        elif moment == 'after_feature':
            hooks.after_feature(context, extra_info)
        elif moment == 'before_scenario':
            hooks.before_scenario(context, extra_info)
        elif moment == 'after_scenario':
            hooks.after_scenario(context, extra_info)
        elif moment == 'before_step':
            hooks.before_step(context, extra_info)
        elif moment == 'after_step':
            hooks.after_step(context, extra_info)
    except (Exception,):
        pass


def generate_simple_html_reports(generate):
    if generate:
        try:
            html_reporter.make_html_reports()
        except (Exception,):
            pass


def generate_html_reports():
    """
        This function generates the html reports.
    :return:
    :rtype:
    """
    try:
        features = []
        with open(f'{BASE_DIR}/output/reports/talos_report.json') as json_file:
            json_data = json.load(json_file)
        for element in json_data.get("features", []):
            new_feature = Feature(
                name=element.get("name"),
                status=element.get("status"),
                tags=element.get("tags", []),
                element_type=Element.ELEMENT_FEATURE,
                location=element.get("location"),
                description=element.get("description"),
                total_scenarios=element.get("total_scenarios"),
                passed_scenarios=element.get("passed_scenarios"),
                failed_scenarios=element.get("failed_scenarios"),
                scenarios_passed_percent=element.get("scenarios_passed_percent"),
                scenarios_failed_percent=element.get("scenarios_failed_percent"),
                total_steps=element.get("total_steps"),
                steps_passed=element.get("steps_passed"),
                steps_failed=element.get("steps_failed"),
                steps_skipped=element.get("steps_skipped"),
                steps_passed_percent=element.get("steps_passed_percent"),
                steps_failed_percent=element.get("steps_failed_percent"),
                steps_skipped_percent=element.get("steps_skipped_percent"),
                start_time=element.get("start_time"),
                end_time=element.get("end_time"),
                duration=element.get("duration", 0),
                driver=element.get("driver"),
                operating_system=element.get("operating_system")
            )
            new_feature.add_elements(element.get("elements"))
            features.append(new_feature)

        HtmlGenerator(features).create_files()
    except (Exception, ) as e:
        traceback.print_exc()


def generate_screenshot(context, step):
    current_driver = str(context.current_driver).lower()
    if current_driver not in ['api', 'backend', 'service']:
        if settings.PYTALOS_REPORTS['generate_screenshot']:
            if current_driver == 'host':
                program_title = context.pytalos_config.get('Driver', 'window_title')
                return get_host_screenshot(program_title)
            else:
                try:
                    return context.utilities.capture_screenshot(
                        f"{str(step.keyword)}_{str(step.name)}"
                    )
                except AttributeError:
                    pass
                except (Exception,):
                    pass


def set_step_info_doc(context, screenshot_path, step):
    current_driver = str(context.current_driver).lower()
    if settings.PYTALOS_REPORTS['generate_docx']:
        if current_driver in ['api', 'backend', 'service'] \
                or 'no_driver' in context.runtime.scenario.tags:
            context.runtime.doc.set_step_info_pre(
                step,
                context.extra_info_dict,
                screenshot_path,
                api_evidence_response=context.api_evidence_response,
                api_evidence_info=context.api_evidence_info,
                api_evidence_headers=context.api_evidence_request_headers,
                api_evidence_body=context.api_evidence_request_body,
                api_evidence_verify=context.api_evidence_verify,
                api_evidence_auto_extra_json=context.api_evidence_auto_extra_json,
                api_evidence_manual_extra_json=context.api_evidence_manual_extra_json
            )

        elif current_driver == 'host':
            context.runtime.doc.set_step_info_pre(
                context.runtime.step,
                context.extra_info_dict,
                screenshot_path,
                api_evidence_manual_extra_json=context.api_evidence_manual_extra_json
            )

        else:
            context.runtime.doc.set_step_info_pre(context.runtime.step, context.extra_info_dict, screenshot_path)


def set_initial_step_data(step):
    """
        This function set new initial data to the step passed in order to avoid errors in the html reports generation.
    :param step:
    :type step:
    :return:
    :rtype:
    """
    step.response_content = None
    step.request = None
    step.screenshots = []
    step.api_evidence_extra_json = None
    step.api_evidence_info = None
    step.api_evidence_verify = None
    step.start_time = datetime.datetime.now().timestamp()
    step.end_time = None
    return step


def set_initial_scenario_data(scenario):
    """
        This function set new initial data to the scenario passed in order to avoid errors in the html reports generation.
    :param scenario:
    :type scenario:
    :return:
    :rtype:
    """
    scenario.start_time = datetime.datetime.now().timestamp()
    scenario.end_time = None
    scenario.total_steps = 0
    scenario.steps_passed = 0
    scenario.steps_failed = 0
    scenario.steps_skipped = 0
    scenario.steps_passed_percent = "0"
    scenario.steps_failed_percent = "0"
    scenario.steps_skipped_percent = "0"
    return scenario


def set_initial_feature_data(context, feature):
    """
        This function set new initial data to the scenario passed in order to avoid errors in the html reports generation.
    :param context:
    :type context:
    :param feature:
    :type feature:
    :return:
    :rtype:
    """
    feature.start_time = datetime.datetime.now().timestamp()
    feature.end_time = None
    feature.driver = context.current_driver
    feature.passed_scenarios = 0
    feature.failed_scenarios = 0
    feature.total_scenarios = 0

    feature.total_steps = 0
    feature.steps_passed = 0
    feature.steps_failed = 0
    feature.steps_skipped = 0

    feature.passed_scenarios = 0
    feature.failed_scenarios = 0
    feature.total_scenarios = 0

    feature.scenarios_passed_percent = "0"
    feature.scenarios_failed_percent = "0"
    feature.steps_passed_percent = "0"
    feature.steps_failed_percent = "0"
    feature.steps_skipped_percent = "0"

    return feature


def add_step_data(context, step, screenshot_path):
    """
        This function add data to the step in order to be reflected in the json file.
    :param context:
    :type context:
    :param step:
    :type step:
    :param screenshot_path:
    :type screenshot_path:
    :return:
    :rtype:
    """
    step.end_time = datetime.datetime.now().timestamp()

    if hasattr(context, "response") and len(context.api_evidence_response) > 0:
        step.request = dict({
            "url": context.response.request.url,
            "headers": context.api_evidence_request_headers,
            "body": context.api_evidence_request_body
        })
        step.response_content = context.api_evidence_response
    step.api_evidence_extra_json = context.api_evidence_manual_extra_json
    step.api_evidence_info = context.api_evidence_info
    step.api_evidence_verify = context.api_evidence_verify

    step.screenshots = [screenshot_path] if screenshot_path is not None else []

    step.screenshots += [text for text in context.extra_info_dict if check_if_string_is_img_route(text)]
    return step


def add_scenario_data(scenario):
    """
        This function add data to the scenario in order to be reflected in the json file.
    :param scenario:
    :type scenario:
    :return:
    :rtype:
    """
    scenario.end_time = datetime.datetime.now().timestamp()
    scenario.total_steps = len(scenario.steps + scenario.background_steps)
    scenario.steps_passed, scenario.steps_failed, scenario.steps_skipped = count_scenario_passed_steps(scenario)

    scenario.steps_passed_percent = "0" if scenario.steps_passed == 0 else format_decimal(
        scenario.steps_passed * 100 / scenario.total_steps)
    scenario.steps_failed_percent = "0" if scenario.steps_failed == 0 else format_decimal(
        scenario.steps_failed * 100 / scenario.total_steps)
    scenario.steps_skipped_percent = "0" if scenario.steps_skipped == 0 else format_decimal(
        scenario.steps_skipped * 100 / scenario.total_steps
    )
    return scenario


def add_feature_data(feature):
    """
        This function add data to the feature in order to be reflected in the json file.
    :param feature:
    :type feature:
    :return:
    :rtype:
    """
    feature.end_time = datetime.datetime.now().timestamp()

    for scenario in feature.scenarios:
        if scenario.type == "scenario" and scenario.status != "skipped":
            if scenario.status == "passed":
                feature.passed_scenarios += 1
            elif scenario.status == "failed":
                feature.failed_scenarios += 1
            feature.total_scenarios += 1

            feature.total_steps += scenario.total_steps
            feature.steps_passed += scenario.steps_passed
            feature.steps_failed += scenario.steps_failed
            feature.steps_skipped += scenario.steps_skipped

        elif scenario.type == "scenario_outline":
            scenarios_list = [_scenario for _scenario in scenario.scenarios if _scenario.status != "skipped"]

            _passed_scenarios, _failed_scenarios, _total_scenarios = count_feature_passed_scenarios(scenarios_list)
            feature.passed_scenarios += _passed_scenarios
            feature.failed_scenarios += _failed_scenarios
            feature.total_scenarios += _total_scenarios

            for scenario_from_scenario_list in scenarios_list:
                feature.total_steps += scenario_from_scenario_list.total_steps
                feature.steps_passed += scenario_from_scenario_list.steps_passed
                feature.steps_failed += scenario_from_scenario_list.steps_failed
                feature.steps_skipped += scenario_from_scenario_list.steps_skipped

    feature.scenarios_passed_percent = "0" if feature.passed_scenarios == 0 else format_decimal(
        feature.passed_scenarios * 100 / feature.total_scenarios)
    feature.scenarios_failed_percent = "0" if feature.failed_scenarios == 0 else format_decimal(
        feature.failed_scenarios * 100 / feature.total_scenarios)

    feature.steps_passed_percent = "0" if feature.steps_passed == 0 else format_decimal(
        feature.steps_passed * 100 / feature.total_steps)
    feature.steps_failed_percent = "0" if feature.steps_failed == 0 else format_decimal(
        feature.steps_failed * 100 / feature.total_steps)
    feature.steps_skipped_percent = "0" if feature.steps_skipped == 0 else format_decimal(
        feature.steps_skipped * 100 / feature.total_steps)

    return feature


def count_scenario_passed_steps(scenario):
    """
        This function counts and return the passed, failed and skipped steps given a scenario object
    :param scenario:
    :type scenario:
    :return:
    :rtype:
    """
    passed_steps = 0
    failed_steps = 0
    skipped_steps = 0
    steps = scenario.steps + scenario.background_steps

    for step in steps:
        if step.status == "passed":
            passed_steps += 1
        elif step.status == "failed":
            failed_steps += 1
        elif step.status == "skipped":
            skipped_steps += 1

    return passed_steps, failed_steps, skipped_steps


def count_feature_passed_scenarios(scenarios):
    """
        This function counts and return the passed, failed and skipped steps given a feature object
    :param scenarios:
    :type scenarios:
    :return:
    :rtype:
    """
    passed_scenarios = 0
    failed_scenarios = 0
    total_scenarios = 0

    for scenario in scenarios:
        if scenario.status == "passed":
            passed_scenarios += 1
            total_scenarios += 1
        else:
            failed_scenarios += 1
            total_scenarios += 1

    return passed_scenarios, failed_scenarios, total_scenarios


def format_decimal(value):
    return f"{value:.2f}"


def check_if_string_is_img_route(string):
    """
        This function check if the string contains the string 'screenshots' and '.png' in order to detect if the string
        passed is a route to an image.
        Its return true or false.
    :param string:
    :type string:
    :return:
    :rtype:
    """
    if "screenshots" in string and ".png" in string:
        return True
    return False
