import argparse
import logging
import os
import re
import shlex
import sys

import six
from behave.configuration import read_configuration, LogLevel
from behave.formatter.base import StreamOpener
from behave.model import ScenarioOutline
from behave.model_core import FileLocation
from behave.reporter.junit import JUnitReporter
from behave.reporter.summary import SummaryReporter
from behave.tag_expression import TagExpression
from behave.textutil import select_best_encoding, to_texts
from behave.userdata import UserData, parse_user_define
from behave.formatter import _registry as _format_registry

from arc.core import constants
from arc.core.env_settings import enabled_proxy

talos_options = [
    (("-c", "--no-color"),
     dict(action="store_false", dest="color",
          help="Disable the use of ANSI color escapes.")),

    (("--color",),
     dict(action="store_true", dest="color",
          help="""Use ANSI color escapes. This is the default
                  behaviour. This switch is used to override a
                  configuration file setting.""")),

    (("-d", "--dry-run"),
     dict(action="store_true",
          help="Invokes formatters without executing the steps.")),

    (("-D", "--define"),
     dict(dest="userdata_defines", type=parse_user_define, action="append",
          metavar="NAME=VALUE",
          help="""Define user-specific data for the config.userdata dictionary.
                  Example: -D foo=bar to store it in config.userdata["foo"].""")),

    (("-e", "--exclude"),
     dict(metavar="PATTERN", dest="exclude_re",
          help="""Don't run feature files matching regular expression
                  PATTERN.""")),

    (("-i", "--include"),
     dict(metavar="PATTERN", dest="include_re",
          help="Only run feature files matching regular expression PATTERN.")),

    (("--no-junit",),
     dict(action="store_false", dest="junit",
          help="Don't output JUnit-compatible reports.")),

    (("--junit",),
     dict(action="store_true",
          help="""Output JUnit-compatible reports.
                  When junit is enabled, all stdout and stderr
                  will be redirected and dumped to the junit report,
                  regardless of the "--capture" and "--no-capture" options.
                  """)),

    (("--junit-directory",),
     dict(metavar="PATH", dest="junit_directory",
          default="reports",
          help="""Directory in which to store JUnit reports.""")),

    ((),  # -- CONFIGFILE only
     dict(dest="default_format",
          help="Specify default formatter (default: pretty).")),

    (("-f", "--format"),
     dict(action="append",
          help="""Specify a formatter. If none is specified the default
                  formatter is used. Pass "--format help" to get a
                  list of available formatters.""")),

    (("--steps-catalog",),
     dict(action="store_true", dest="steps_catalog",
          help="""Show a catalog of all available step definitions.
                  SAME AS: --format=steps.catalog --dry-run --no-summary -q""")),

    ((),  # -- CONFIGFILE only
     dict(dest="scenario_outline_annotation_schema",
          help="""Specify name annotation schema for scenario outline
                  (default="{name} -- @{row.id} {examples.name}").""")),

    (("-k", "--no-skipped"),
     dict(action="store_false", dest="show_skipped",
          help="Don't print skipped steps (due to tags).")),

    (("--show-skipped",),
     dict(action="store_true",
          help="""Print skipped steps.
                  This is the default behaviour. This switch is used to
                  override a configuration file setting.""")),

    (("--no-snippets",),
     dict(action="store_false", dest="show_snippets",
          help="Don't print snippets for unimplemented steps.")),
    (("--snippets",),
     dict(action="store_true", dest="show_snippets",
          help="""Print snippets for unimplemented steps.
                  This is the default behaviour. This switch is used to
                  override a configuration file setting.""")),

    (("-m", "--no-multiline"),
     dict(action="store_false", dest="show_multiline",
          help="""Don't print multiline strings and tables under
                  steps.""")),

    (("--multiline",),
     dict(action="store_true", dest="show_multiline",
          help="""Print multiline strings and tables under steps.
                  This is the default behaviour. This switch is used to
                  override a configuration file setting.""")),

    (("-n", "--name"),
     dict(action="append",
          help="""Only execute the feature elements which match part
                  of the given name. If this option is given more
                  than once, it will match against all the given
                  names.""")),

    (("--no-capture",),
     dict(action="store_false", dest="stdout_capture",
          help="""Don't capture stdout (any stdout output will be
                  printed immediately.)""")),

    (("--capture",),
     dict(action="store_true", dest="stdout_capture",
          help="""Capture stdout (any stdout output will be
                  printed if there is a failure.)
                  This is the default behaviour. This switch is used to
                  override a configuration file setting.""")),

    (("--no-capture-stderr",),
     dict(action="store_false", dest="stderr_capture",
          help="""Don't capture stderr (any stderr output will be
                  printed immediately.)""")),

    (("--capture-stderr",),
     dict(action="store_true", dest="stderr_capture",
          help="""Capture stderr (any stderr output will be
                  printed if there is a failure.)
                  This is the default behaviour. This switch is used to
                  override a configuration file setting.""")),

    (("--no-logcapture",),
     dict(action="store_false", dest="log_capture",
          help="""Don't capture logging. Logging configuration will
                  be left intact.""")),

    (("--logcapture",),
     dict(action="store_true", dest="log_capture",
          help="""Capture logging. All logging during a step will be captured
                  and displayed in the event of a failure.
                  This is the default behaviour. This switch is used to
                  override a configuration file setting.""")),

    (("--logging-level",),
     dict(type=LogLevel.parse_type,
          help="""Specify a level to capture logging at. The default
                  is INFO - capturing everything.""")),

    (("--logging-format",),
     dict(help="""Specify custom format to print statements. Uses the
                  same format as used by standard logging handlers. The
                  default is "%%(levelname)s:%%(name)s:%%(message)s".""")),

    (("--logging-datefmt",),
     dict(help="""Specify custom date/time format to print
                  statements.
                  Uses the same format as used by standard logging
                  handlers.""")),

    (("--logging-filter",),
     dict(help="""Specify which statements to filter in/out. By default,
                  everything is captured. If the output is too verbose, use
                  this option to filter out needless output.
                  Example: --logging-filter=foo will capture statements issued
                  ONLY to foo or foo.what.ever.sub but not foobar or other
                  logger. Specify multiple loggers with comma:
                  filter=foo,bar,baz.
                  If any logger name is prefixed with a minus, eg filter=-foo,
                  it will be excluded rather than included.""",
          config_help="""Specify which statements to filter in/out. By default,
                         everything is captured. If the output is too verbose,
                         use this option to filter out needless output.
                         Example: ``logging_filter = foo`` will capture
                         statements issued ONLY to "foo" or "foo.what.ever.sub"
                         but not "foobar" or other logger. Specify multiple
                         loggers with comma: ``logging_filter = foo,bar,baz``.
                         If any logger name is prefixed with a minus, eg
                         ``logging_filter = -foo``, it will be excluded rather
                         than included.""")),

    (("--logging-clear-handlers",),
     dict(action="store_true",
          help="Clear all other logging handlers.")),

    (("--no-summary",),
     dict(action="store_false", dest="summary",
          help="""Don't display the summary at the end of the run.""")),

    (("--summary",),
     dict(action="store_true", dest="summary",
          help="""Display the summary at the end of the run.""")),

    (("-o", "--outfile"),
     dict(action="append", dest="outfiles", metavar="FILE",
          help="Write to specified file instead of stdout.")),

    ((),  # -- CONFIGFILE only
     dict(action="append", dest="paths",
          help="Specify default feature paths, used when none are provided.")),

    (("-q", "--quiet"),
     dict(action="store_true",
          help="Alias for --no-snippets --no-source.")),

    (("-s", "--no-source"),
     dict(action="store_false", dest="show_source",
          help="""Don't print the file and line of the step definition with the
                  steps.""")),

    (("--show-source",),
     dict(action="store_true", dest="show_source",
          help="""Print the file and line of the step
                  definition with the steps. This is the default
                  behaviour. This switch is used to override a
                  configuration file setting.""")),

    (("--stage",),
     dict(help="""Defines the current test stage.
                  The test stage name is used as name prefix for the environment
                  file and the steps directory (instead of default path names).
                  """)),

    (("--stop",),
     dict(action="store_true",
          help="Stop running tests at the first failure.")),

    ((),  # -- CONFIGFILE only
     dict(dest="default_tags", metavar="TAG_EXPRESSION",
          help="""Define default tags when non are provided.
                  See --tags for more information.""")),

    (("-t", "--tags"),
     dict(action="append", metavar="TAG_EXPRESSION",
          help="""Only execute features or scenarios with tags
                  matching TAG_EXPRESSION. Pass "--tags-help" for
                  more information.""",
          config_help="""Only execute certain features or scenarios based
                         on the tag expression given. See below for how to code
                         tag expressions in configuration files.""")),

    (("-T", "--no-timings"),
     dict(action="store_false", dest="show_timings",
          help="""Don't print the time taken for each step.""")),

    (("--show-timings",),
     dict(action="store_true", dest="show_timings",
          help="""Print the time taken, in seconds, of each step after the
                  step has completed. This is the default behaviour. This
                  switch is used to override a configuration file
                  setting.""")),

    (("-v", "--verbose"),
     dict(action="store_true",
          help="Show the files and features loaded.")),

    (("-w", "--wip"),
     dict(action="store_true",
          help="""Only run scenarios tagged with "wip". Additionally: use the
                  "plain" formatter, do not capture stdout or logging output
                  and stop at the first failure.""")),

    (("-x", "--expand"),
     dict(action="store_true",
          help="Expand scenario outline tables in output.")),

    (("--lang",),
     dict(metavar="LANG",
          help="Use keywords for a language other than English.")),

    (("--lang-list",),
     dict(action="store_true",
          help="List the languages available for --lang.")),

    (("--lang-help",),
     dict(metavar="LANG",
          help="List the translations accepted for one language.")),

    (("--tags-help",),
     dict(action="store_true",
          help="Show help for tag expressions.")),

    (("--version",),
     dict(action="store_true", help="Show version.")),

    (("-p", "--proxy"),
     dict(action="append", dest="proxy",
          help="Provides a proxy for execution.")),

    (("-env", "--environment"),
     dict(action="append", dest="environment",
          help="Provide the name of the environment for the profile data.")),
]


def setup_custom_parser():
    # construct the parser
    # usage = "%(prog)s [options] [ [FILE|DIR|URL][:LINE[:LINE]*] ]+"
    usage = "%(prog)s [options] [ [DIR|FILE|FILE:LINE] ]+ error"
    description = """\
    Run a number of feature tests with behave."""
    more = """
    EXAMPLES:
    behave features/
    behave features/one.feature features/two.feature
    behave features/one.feature:10
    behave @features.txt
    """
    parser = argparse.ArgumentParser(usage=usage, description=description)
    for fixed, keywords in talos_options:
        if not fixed:
            continue  # -- CONFIGFILE only.
        if "config_help" in keywords:
            keywords = dict(keywords)
            del keywords["config_help"]
        parser.add_argument(*fixed, **keywords)
    parser.add_argument("paths", nargs="*",
                        help="Feature directory, file or file location (FILE:LINE).")

    return parser


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


def load_configuration_override(defaults, settings, verbose=False):
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


class BehaveConfiguration:
    defaults = dict(
        color=sys.platform != "win32",
        show_snippets=True,
        show_skipped=True,
        dry_run=False,
        show_source=True,
        show_timings=True,
        stdout_capture=True,
        stderr_capture=True,
        log_capture=True,
        logging_format="%(levelname)s:%(name)s:%(message)s",
        logging_level=logging.INFO,
        steps_catalog=False,
        summary=True,
        junit=False,
        stage=None,
        userdata={},
        # -- SPECIAL:
        default_format="pretty",  # -- Used when no formatters are configured.
        default_tags="",  # -- Used when no tags are defined.
        scenario_outline_annotation_schema=u"{name} -- @{row.id} {examples.name}",
        proxy=None,
        environment=None
    )

    cmdline_only_options = set("userdata_defines")

    def __init__(self, command_args=None, load_config=True, verbose=None, run_settings=None,
                 **kwargs):

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
        self.proxy = None
        self.environment = None

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
            load_configuration_override(self.defaults, run_settings, verbose=verbose)
        parser = setup_custom_parser()
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

        if self.proxy:
            http = self.proxy[0]
            https = self.proxy[0]
            # enabled_proxy(http, https)
            run_settings.PYTALOS_RUN['execution_proxy']['enabled'] = True
            run_settings.PYTALOS_RUN['execution_proxy']['proxy']['http_proxy'] = http
            run_settings.PYTALOS_RUN['execution_proxy']['proxy']['https_proxy'] = https
        # else:
        #     # if run_settings.PYTALOS_RUN['execution_proxy']['enabled']:
        #     #     http = run_settings.PYTALOS_RUN['execution_proxy']['proxy']['http_proxy']
        #     #     https = run_settings.PYTALOS_RUN['execution_proxy']['proxy']['https_proxy']
        #     #     enabled_proxy(http, https)
        #     pass

        if self.environment:
            run_settings.PYTALOS_PROFILES['environment'] = self.environment[0]

    def setup_outputs(self, args_outfiles=None):
        if self.outputs:
            assert not args_outfiles, "ONLY-ONCE"
            return

        # -- NORMAL CASE: Setup only initially (once).
        if not args_outfiles:
            self.outputs.append(StreamOpener(stream=sys.stdout))
        else:
            for outfile in args_outfiles:
                if outfile and outfile != "-":
                    self.outputs.append(StreamOpener(outfile))
                else:
                    self.outputs.append(StreamOpener(stream=sys.stdout))

    def setup_formats(self):
        if self.more_formatters:
            for name, scoped_class_name in self.more_formatters.items():
                _format_registry.register_as(name, scoped_class_name)

    def collect_unknown_formats(self):
        unknown_formats = []
        if self.format:
            for format_name in self.format:
                if (format_name == "help" or
                        _format_registry.is_formatter_valid(format_name)):
                    continue
                unknown_formats.append(format_name)
        return unknown_formats

    @staticmethod
    def build_name_re(names):
        # -- NOTE: re.LOCALE is removed in Python 3.6 (deprecated in Python 3.5)
        # flags = (re.UNICODE | re.LOCALE)
        # -- ENSURE: Names are all unicode/text values (for issue #606).
        names = to_texts(names)
        pattern = u"|".join(names)
        return re.compile(pattern, flags=re.UNICODE)

    def exclude(self, filename):
        if isinstance(filename, FileLocation):
            filename = six.text_type(filename)

        if self.include_re and self.include_re.search(filename) is None:
            return True
        if self.exclude_re and self.exclude_re.search(filename) is not None:
            return True
        return False

    def setup_logging(self, level=None, configfile=None, **kwargs):
        if level is None:
            level = self.logging_level  # pylint: disable=no-member

        if configfile:
            from logging.config import fileConfig
            fileConfig(configfile)
        else:
            # pylint: disable=no-member
            format_ = kwargs.pop("format", self.logging_format)
            datefmt = kwargs.pop("datefmt", self.logging_datefmt)
            logging.basicConfig(format=format_, datefmt=datefmt, **kwargs)
        # -- ENSURE: Default log level is set
        #    (even if logging subsystem is already configured).
        logging.getLogger().setLevel(level)

    def setup_model(self):
        if self.scenario_outline_annotation_schema:
            name_schema = six.text_type(self.scenario_outline_annotation_schema)
            ScenarioOutline.annotation_schema = name_schema.strip()

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

    def update_userdata(self, data):
        self.userdata.update(data)
        if self.userdata_defines:
            # -- REAPPLY: Cmd-line defines (override configuration file data).
            self.userdata.update(self.userdata_defines)


def set_report_configuration(settings):
    if settings.PYTALOS_REPORTS['generate_extra_reports']:
        settings.BEHAVE['format'] = constants.BEHAVE_FORMAT
        settings.BEHAVE['outfiles'] = constants.BEHAVE_OUTFILES

    settings.BEHAVE['junit_directory'] = 'output/reports/html'
