# -*- coding: utf-8 -*-
import datetime

from behave.__main__ import run_behave
from behave._types import ExceptionUtil
from behave.capture import CaptureController
from behave.runner import ModelRunner, Runner
from behave.runner_util import PathManager

from arc.core.behave.configuration import BehaveConfiguration, set_report_configuration
from arc.environment import after_execution, before_execution
from arc.misc import title
from arc.core import constants
try:
    from settings import settings
except (Exception,):
    from arc.settings import settings


class CustomModelRunner(ModelRunner):

    def __init__(self, config, features=None, step_registry=None):
        super(CustomModelRunner, self).__init__(config)
        self.config = config
        self.features = features or []
        self.hooks = {}
        self.formatters = []
        self.undefined_steps = []
        self.step_registry = step_registry
        self.capture_controller = CaptureController(config)

        self.context = None
        self.feature = None
        self.hook_failures = 0

    def run_hook(self, name, context, *args):
        if not self.config.dry_run and (name in self.hooks):
            try:
                with context.use_with_user_mode():
                    self.hooks[name](context, *args)
            except KeyboardInterrupt:
                self.aborted = True
                if name not in ("before_all", "after_all"):
                    raise
            except Exception as e:
                use_traceback = True
                ExceptionUtil.set_traceback(e)
                extra = u""
                if "tag" in name:
                    extra = "(tag=%s)" % args[0]

                error_text = ExceptionUtil.describe(e, use_traceback).rstrip()
                error_message = u"\nHOOK-ERROR in %s%s: %s" % (name, extra, error_text)
                print(error_message)
                self.hook_failures += 1
                if "tag" in name:
                    statement = getattr(context, "scenario", context.feature)
                elif "all" in name:
                    self.aborted = True
                    statement = None
                else:
                    statement = args[0]

                if statement:
                    statement.hook_failed = True
                    if statement.error_message:
                        statement.error_message += u"\n" + error_message
                    else:
                        statement.store_exception_context(e)
                        statement.error_message = error_message


class CustomRunner(CustomModelRunner, Runner):

    def __init__(self, config):
        super(Runner, self).__init__(config)
        self.path_manager = PathManager()
        self.base_dir = None


def make_behave_argv(verbose: bool = False, junit: bool = False, format_pretty: bool = False,
                     formatter: str = None, output: str = None, tags: [str, list] = None, conf_properties: str = None,
                     features_dir: str = None, allure: bool = False, teamcity: bool = False, **kwargs):
    params = ''
    if verbose:
        params = params + ' -v'
    if junit:
        params = params + ' --junit'
    if format_pretty:
        params = params + ' --format pretty'
    if formatter:
        params = params + ' -f ' + formatter
    if output:
        params = params + ' -o ' + output
    if tags:
        params = ''.join(' --tags=' + ','.join(tag if isinstance(tag, list) else [tag]) for tag in
                         (tags if isinstance(tags, list) else [tags])).replace(', ', ',')
    if conf_properties:
        params = params + ' -D Config_environment=' + conf_properties
    if kwargs:
        for k, v in kwargs.items():
            params = params + ' -D ' + k + '=' + v
    if features_dir:
        params = params + ' ' + features_dir

    if allure:
        params = params + " -f allure_behave.formatter:AllureFormatter -o output/info/allure"

    if teamcity:
        params = params + " -f behave_teamcity:TeamcityFormatter -o output/info/teamcity"

    return params


def add_extra_args(args):
    args += constants.BEHAVE_ARGS['TALOS_JSON_REPORT']
    return args


def main(args=None):
    before_execution()
    set_report_configuration(settings)
    args = add_extra_args(args)
    config = BehaveConfiguration(command_args=args, run_settings=settings)
    print('Started at:', datetime.datetime.now())
    title()
    finish_code = run_behave(config, CustomRunner)
    after_execution()
    print('Ended at:', datetime.datetime.now())
    return finish_code
