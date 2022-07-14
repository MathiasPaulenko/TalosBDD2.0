# -*- coding: utf-8 -*-
import datetime

from behave.model import Scenario

from arc.integrations.alm import run_alm_connect
from settings import settings
from arc.contrib import func
from arc.contrib.api import api_wrapper
from arc.contrib.db import sqlite
from arc.contrib.tools import ftp
from arc.core.behave import config_data, gherkin_format, env_utils
from arc.core.behave.context_utils import RuntimeDatas, Settings, TestData
from arc.core.behave.env_utils import (
    set_reporting_config_path,
    enable_jira_report,
    config_faker,
    enable_txt_report,
    run_hooks,
    enable_json_report,
    enable_doc_report,
    enable_host, close_host, set_doc_info_and_end, set_doc_note,
    set_alm_custom_variable, generate_screenshot, set_initial_scenario_data, set_initial_feature_data,
    add_scenario_data, add_feature_data, set_initial_step_data, add_step_data, generate_simple_html_reports,
    generate_html_reports
)
from arc.core.behave.environment import (
    before_all as core_before_all,
    before_feature as core_before_feature,
    before_scenario as core_before_scenario,
    after_scenario as core_after_scenario,
    after_feature as core_after_feature,
    after_all as core_after_all
)
from arc.core.paths.directories import enable_delete_old_reports, generate_needed_dir
from arc.core.paths.drivers import add_drivers_directory_to_path
from arc.reports.catalog import excel_catalog
from arc.contrib.utilities import Utils


def before_execution():
    run_hooks(context=None, moment='before_execution')


def before_all(context):
    # core task
    core_before_all(context)

    # set core context functionalities
    context.runtime = RuntimeDatas(context)
    context.settings = Settings(context)
    context.test = TestData(context)
    context.runtime.master_file = settings.PYTALOS_PROFILES['master_file']
    context.current_driver = context.pytalos_config.get('Driver', 'type')
    context.runtime.current_date = datetime.datetime.now()
    context.fake_data = config_faker()
    context.sqlite = sqlite.sqlite_db()

    # run before all functionalities
    Scenario.continue_after_failed_step = settings.PYTALOS_RUN['continue_after_failed_step']
    add_drivers_directory_to_path()
    enable_delete_old_reports(settings.PYTALOS_RUN['delete_old_reports'])
    generate_needed_dir(context.current_driver)
    set_reporting_config_path(context)

    # enable reporting
    context.runtime.jira = enable_jira_report()
    context.runtime.txt_log = enable_txt_report()

    # run hooks
    run_hooks(context, 'before_all')

    context.logger.debug(f"the core before all actions have been executed correctly")


def before_feature(context, feature):
    # core task
    core_before_feature(context, feature)
    set_initial_feature_data(context, feature)

    # add log txt info
    if settings.PYTALOS_REPORTS['generate_txt']:
        context.runtime.txt_log.write_before_feature_info(feature)

    # run hooks
    run_hooks(context, 'before_feature')

    context.logger.debug(f"the core before feature actions have been executed correctly")


def before_scenario(context, scenario):
    # core task
    core_before_scenario(context, scenario)
    set_initial_scenario_data(scenario)

    # set core context functionalities
    context.runtime.scenario = scenario
    context.utilities = Utils()
    context.func = func.Func(context)

    # run before scenario functionalities
    config_data.get_datas(context)
    gherkin_format.generate_scenario_description(scenario)

    # enable reporting
    context.runtime.alm_json = enable_json_report(scenario)
    context.runtime.doc = enable_doc_report(scenario)

    # enable automation functionalities
    enable_host(context)
    context.api = api_wrapper.ApiObject(context)
    context.ftp = ftp.FtpObject(context)

    # run hooks
    run_hooks(context, 'before_scenario')

    context.logger.debug(f"the core before scenario actions have been executed correctly")


def after_scenario(context, scenario):
    # core task
    core_after_scenario(context, scenario)
    add_scenario_data(scenario)

    # reporting actions
    doc_path = set_doc_info_and_end(context, scenario)

    if settings.PYTALOS_ALM['generate_json']:
        context.runtime.alm_json.generate_json_after_scenario(
            scenario, doc_path, generate_html_report=settings.PYTALOS_REPORTS['generate_html']
        )

    if settings.PYTALOS_REPORTS['generate_txt']:
        context.runtime.txt_log.write_scenario_info(scenario)

    if settings.PYTALOS_JIRA['post_to_jira']:
        context.runtime.jira.set_scenario(scenario, doc_path)

    # automation actions
    close_host(context)

    # run hooks
    run_hooks(context, 'after_scenario')

    context.logger.debug(f"the core after scenario actions have been executed correctly")


def after_feature(context, feature):
    # core task
    core_after_feature(context, feature)

    # reporting actions
    if settings.PYTALOS_REPORTS['generate_txt']:
        context.runtime.txt_log.write_after_feature_info(feature)

    add_feature_data(feature)

    # run hooks
    run_hooks(context, 'after_feature')

    context.logger.debug(f"the core after feature actions have been executed correctly")


def after_all(context):
    # core task
    core_after_all(context)

    # reporting actions
    generate_simple_html_reports(settings.PYTALOS_REPORTS['generate_simple_html'])
    run_alm_connect()

    if settings.PYTALOS_REPORTS['generate_txt']:
        context.runtime.txt_log.write_summary()

    if settings.PYTALOS_JIRA['post_to_jira']:
        context.runtime.jira.post_to_jira()

    # catalog generation
    if settings.PYTALOS_CATALOG['update_step_catalog']:
        excel_catalog.Catalog()

    # run hooks
    run_hooks(context, 'after_all')

    context.logger.debug(f"the core after all actions have been executed correctly")


def before_step(context, step):
    # set core context functionalities
    context.runtime.step = step
    set_alm_custom_variable(context)

    # reporting actions
    set_doc_note(settings.PYTALOS_REPORTS['generate_docx'], context)

    # api evidence
    # TODO: refactorizar
    context.extra_info_dict = []
    context.api_evidence_response = []
    context.api_evidence_info = {}
    context.api_evidence_request_headers = {}
    context.api_evidence_auto_extra_json = []
    context.api_evidence_manual_extra_json = []
    context.api_evidence_request_body = []
    context.api_evidence_verify = []
    set_initial_step_data(step)

    # run hooks
    run_hooks(context, 'before_step')


def after_step(context, step):
    # reporting actions
    screenshot_path = generate_screenshot(context, step)
    env_utils.set_step_info_doc(context, screenshot_path, step)

    if settings.PYTALOS_ALM['generate_json']:
        context.runtime.alm_json.generate_json_after_step(step)
    add_step_data(context, step, screenshot_path)

    # run hooks
    run_hooks(context, 'after_step')


def after_execution():
    if settings.PYTALOS_REPORTS.get('generate_html', False):
        generate_html_reports()

    run_hooks(context=None, moment='after_execution')
