# -*- coding: utf-8 -*-

#: Operative Systems
XP = 'XP'
W7 = 'VISTA'
W8 = 'WIN8'
W10 = 'WIN10'
LINUX = 'LINUX'
ANDROID = 'android'
IOS = 'ios'
IPHONE = 'iphone'
MAC = 'MAC'

#: Drivers
OPERA = 'opera'
FIREFOX = 'firefox'
CHROME = 'chrome'
SAFARI = 'safari'
IEXPLORE = 'iexplore'
EDGE = 'edge'
PHANTOMJS = 'phantomjs'
EDGEIE = 'edgeie'

#: Selenoid
SEL_STATUS_OK = 200
SEL_STATUS_PORT = "8888"
SEL_DOWNLOADS_PATH = u'downloads'
SEL_MP4_EXTENSION = u'mp4'
SEL_LOG_EXTENSION = u'log'

#: Commons
FILENAME_MAX_LENGTH = 100

#: Behave
ACTIONS_BEFORE_FEATURE = u'actions before the feature'
ACTIONS_BEFORE_SCENARIO = u'actions before each scenario'
ACTIONS_AFTER_SCENARIO = u'actions after each scenario'
ACTIONS_AFTER_FEATURE = u'actions after the feature'
KEYWORDS = [u'Setup', u'Check', u'Given', u'When', u'Then', u'And', u'But']
GIVEN_PREFIX = u'Given'
TABLE_SEPARATOR = u'|'
EMPTY = u''

#: Behave Reporting
BEHAVE_FORMAT = [
    'pretty',
    'plain',
    'progress3',
    'json.pretty',
    'json',
    'rerun',
    'sphinx.steps',
    'steps',
    'steps.doc',
    'steps.usage',
    'tags',
    'tags.location',
]

BEHAVE_OUTFILES = [
    'output/info/features_pretty.txt',
    'output/info/features_plain.txt',
    'output/info/features_progress.txt',
    'output/info/behave_json_pretty.json',
    'output/info/behave_json.json',
    'output/info/scenario_failed.txt',
    'output/info/steps_rst',
    'output/info/steps_list.txt',
    'output/info/steps_definition.txt',
    'output/info/steps_usage.txt',
    'output/info/tags_usage.txt',
    'output/info/tags_location.txt',
]

BEHAVE_ARGS = {
    'TALOS_JSON_REPORT': ' -f arc.reports.custom_formatters:CustomJSONFormatter '
                         '-o output/reports/talos_report.json --format pretty',
}
