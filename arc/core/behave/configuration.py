import os
import re
import shlex
import sys

import six
from behave.configuration import Configuration, read_configuration, setup_parser
from behave.reporter.junit import JUnitReporter
from behave.reporter.summary import SummaryReporter
from behave.tag_expression import TagExpression
from behave.textutil import select_best_encoding, to_texts
from behave.userdata import UserData

from settings import settings


def config_filenames_override(path=None):
    # TODO: This line will have to be changed when pytalos will be a pip library
    # paths = ["./", os.path.expanduser("~"), os.path.abspath("settings") + os.sep]
    # Introducing the path where the behave.ini will be inside the TalosBDD project
    # You will also have to see the default values of the behave.ini and the outputs of the logs
    if path:
        paths = ["./", os.path.expanduser("~"), path]
    else:
        paths = ["./", os.path.expanduser("~"), os.path.abspath("arc/settings") + os.sep]

    if sys.platform in ("cygwin", "win32") and "APPDATA" in os.environ:
        paths.append(os.path.join(os.environ["APPDATA"]))

    for path in reversed(paths):
        for filename in reversed(
                ("behave.ini", ".behaverc", "setup.cfg", "tox.ini")):
            filename = os.path.join(path, filename)
            if os.path.isfile(filename):
                yield filename


def load_configuration_override(defaults, verbose=False):
    try:
        if hasattr(settings, "BEHAVE_INIT_PATH"):
            for filename in config_filenames_override(path=settings.BEHAVE_INIT_PATH):
                if verbose:
                    print(f"Loading config defaults from {filename}")
                defaults.update(read_configuration(filename))

        elif hasattr(settings, 'BEHAVE'):
            defaults.update(settings.BEHAVE)
        else:
            raise
    except (Exception,):
        for filename in config_filenames_override():
            if verbose:
                print(f"Loading config defaults from {filename}")
            defaults.update(read_configuration(filename))

    if verbose:
        print("Using defaults:")
        for k, v in six.iteritems(defaults):
            print("%15s %s" % (k, v))


class BehaveConfiguration(Configuration):

    def __init__(self, command_args=None, load_config=True, verbose=None,
                 **kwargs):
        super(BehaveConfiguration, self).__init__()
        if command_args is None:
            command_args = sys.argv[1:]
        elif isinstance(command_args, six.string_types):
            encoding = select_best_encoding() or "utf-8"
            if six.PY2 and isinstance(command_args, six.text_type):
                command_args = command_args.encode(encoding)
            elif six.PY3 and isinstance(command_args, six.binary_type):
                command_args = command_args.decode(encoding)
            command_args = shlex.split(command_args)
        elif isinstance(command_args, (list, tuple)):
            command_args = to_texts(command_args)

        if verbose is None:
            verbose = ("-v" in command_args) or ("--verbose" in command_args)

        self.version = None
        self.tags_help = None
        self.lang_list = None
        self.lang_help = None
        self.default_tags = None
        self.junit = None
        self.logging_format = None
        self.logging_datefmt = None
        self.name = None
        self.scope = None
        self.steps_catalog = None
        self.userdata = None
        self.wip = None

        defaults = self.defaults.copy()
        for name, value in six.iteritems(kwargs):
            defaults[name] = value
        self.defaults = defaults
        self.formatters = []
        self.reporters = []
        self.name_re = None
        self.outputs = []
        self.include_re = None
        self.exclude_re = None
        self.scenario_outline_annotation_schema = None
        self.steps_dir = "steps"
        self.environment_file = "environment.py"
        self.userdata_defines = None
        self.more_formatters = None
        if load_config:
            load_configuration_override(self.defaults, verbose=verbose)
        parser = setup_parser()
        parser.set_defaults(**self.defaults)
        args = parser.parse_args(command_args)
        for key, value in six.iteritems(args.__dict__):
            if key.startswith("_") and key not in self.cmdline_only_options:
                continue
            setattr(self, key, value)

        self.paths = [os.path.normpath(path) for path in self.paths]
        self.setup_outputs(args.outfiles)

        if self.steps_catalog:
            self.default_format = "steps.catalog"
            self.format = ["steps.catalog"]
            self.dry_run = True
            self.summary = False
            self.show_skipped = False
            self.quiet = True

        if self.wip:
            self.default_format = "plain"
            self.tags = ["wip"] + self.default_tags.split()
            self.color = False
            self.stop = True
            self.log_capture = False
            self.stdout_capture = False

        self.tags = TagExpression(self.tags or self.default_tags.split())

        if self.quiet:
            self.show_source = False
            self.show_snippets = False

        if self.exclude_re:
            self.exclude_re = re.compile(self.exclude_re)

        if self.include_re:
            self.include_re = re.compile(self.include_re)
        if self.name:
            self.name_re = self.build_name_re(self.name)

        if self.stage is None:
            self.stage = os.environ.get("BEHAVE_STAGE", None)
        self.setup_stage(self.stage)
        self.setup_model()
        self.setup_userdata()

        if self.junit:
            self.stdout_capture = True
            self.stderr_capture = True
            self.log_capture = True
            self.reporters.append(JUnitReporter(self))
        if self.summary:
            self.reporters.append(SummaryReporter(self))

        self.setup_formats()
        unknown_formats = self.collect_unknown_formats()
        if unknown_formats:
            parser.error("format=%s is unknown" % ", ".join(unknown_formats))

    def setup_stage(self, stage=None):
        steps_dir = "test/steps"
        environment_file = "arc/environment.py"
        if stage:
            prefix = stage + "_"
            steps_dir = prefix + steps_dir
            environment_file = prefix + environment_file
        self.steps_dir = steps_dir
        self.environment_file = environment_file

    def setup_userdata(self):
        if not isinstance(self.userdata, UserData):
            self.userdata = UserData(self.userdata)
        if self.userdata_defines:
            self.userdata.update(self.userdata_defines)
