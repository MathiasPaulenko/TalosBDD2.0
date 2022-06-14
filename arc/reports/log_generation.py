import os
import time

from settings import settings

BASE_PATH = os.path.abspath(os.path.join(os.path.abspath(__file__), os.pardir)) + os.sep
LOG_PATH = os.path.abspath("output") + os.sep + "logs" + os.sep

NL = '\n'
TAB = '\t'
PROMPT = '-->'
SEP = f'{TAB}:{TAB}'
HR = f"-----------------------------------------------------------------------{NL}"
DHR = f"======================================================================={NL}"
PASSED = 'PASSED'
FAILED = 'FAILED'


class ExecutionTxtLog:
    scenario_info_list: list
    scenario_tags: list
    scenario_passed = 0
    scenario_failed = 0
    scenario_skipped = 0
    feature_passed = 0
    feature_failed = 0
    feature_skipped = 0
    total_feature_duration = 0

    def __init__(self):
        self.log_file = open(LOG_PATH + f'execution_log.txt', 'w+', encoding='UTF8')
        self.write_title()
        self.write_title_total_execution()

    def write_summary(self):
        feature_duration = time.strftime('%H:%M:%S', time.gmtime(self.total_feature_duration))
        feature_total = self.feature_failed + self.feature_passed + self.feature_skipped
        scenario_total = self.scenario_failed + self.scenario_passed + self.scenario_skipped
        self.log_file.write(f"Final results{NL}")
        self.log_file.write(DHR)
        self.log_file.write(f'Total Features{TAB}{TAB}{SEP}{feature_total}{NL}')
        self.log_file.write(f'Features Passed{TAB}{TAB}{SEP}{self.feature_passed}{NL}')
        self.log_file.write(f'Features Failed{TAB}{TAB}{SEP}{self.feature_failed}{NL}')
        self.log_file.write(f'Features Skipped{TAB}{SEP}{self.feature_skipped}{NL}')
        try:
            self.log_file.write(f'Feature success rate{SEP}{(self.feature_passed * 100) / feature_total}%{NL}')
        except ZeroDivisionError:
            pass
        self.log_file.write(HR)
        self.log_file.write(f'Total Scenarios{TAB}{TAB}{SEP}{scenario_total}{NL}')
        self.log_file.write(f'Scenarios Passed{TAB}{SEP}{self.scenario_passed}{NL}')
        self.log_file.write(f'Scenarios Failed{TAB}{SEP}{self.scenario_failed}{NL}')
        self.log_file.write(f'Scenarios Skipped{TAB}{SEP}{self.scenario_skipped}{NL}')
        try:
            self.log_file.write(f'Scenario success rate{SEP}{(self.scenario_passed * 100) / scenario_total}%{NL}')
        except ZeroDivisionError:
            pass
        self.log_file.write(HR)
        self.log_file.write(f'Total Duration{TAB}{TAB}{SEP}{feature_duration}{NL}')
        self.log_file.write(DHR)
        self.close_file()

    def write_scenario_info(self, scenario):
        scenario_status = f"{str(scenario.status).split('.')[1].upper()}"
        duration = f"{time.strftime('%H:%M:%S', time.gmtime(scenario.duration))}"
        self.log_file.write(f'{PROMPT} {scenario_status}{SEP}{duration}{SEP}{scenario.name}{NL}')
        self.add_scenario_result(scenario_status)
        self.add_scenario_tags(scenario.tags)

    def write_before_feature_info(self, feature):
        if settings.PYTALOS_REPORTS['generate_txt']:
            self.log_file.write(f"Feature Name: {feature.name}{NL}")
            self.log_file.write(HR)
            self.log_file.write(
                f"Description:{NL}{TAB}- {f'{NL}{TAB}- '.join(str(x) for x in feature.description)}{NL}")
            self.log_file.write(f"Tags: {', '.join(str(x) for x in feature.tags)}{NL}")
            self.log_file.write(f"Information:{NL}")
            self.log_file.write(f"{TAB}- Location: {feature.filename} : {feature.line}{NL}")
            self.log_file.write(f"{TAB}- Language: {feature.language}{NL}")
            self.log_file.write(HR)
            self.scenario_tags = []

    def write_after_feature_info(self, feature):
        duration = f"{time.strftime('%H:%M:%S', time.gmtime(feature.duration))}"
        feature_status = f"{str(feature.status).split('.')[1].upper()}"
        self.log_file.write(HR)
        self.log_file.write(f"Feature Result: {feature_status}{SEP}Duration: {duration}{NL}")
        if self.scenario_tags:
            self.log_file.write(f"Executed Scenario Tags{SEP}{', '.join(str(x) for x in self.scenario_tags)}{NL}")
        if feature.hook_failed:
            self.log_file.write(f"Error: {str(feature.hook_failed)}{NL}")
        self.log_file.write(HR)
        self.log_file.write(f'{NL}{NL}')
        self.add_feature_result(feature_status)
        self.add_total_duration(feature.duration)

    def add_scenario_result(self, scenario_status):
        if scenario_status == PASSED:
            self.scenario_passed += 1
        elif scenario_status == FAILED:
            self.scenario_failed += 1
        else:
            self.scenario_skipped += 1

    def add_feature_result(self, feature_status):
        if feature_status == PASSED:
            self.feature_passed += 1
        elif feature_status == FAILED:
            self.feature_failed += 1
        else:
            self.feature_skipped += 1

    def add_total_duration(self, duration):
        self.total_feature_duration += duration

    def add_scenario_tags(self, tags_list):
        for tag in tags_list:
            if tag not in self.scenario_tags:
                self.scenario_tags.append(tag)

    def close_file(self):
        self.log_file.close()

    def write_title(self):
        self.log_file.write(DHR)
        self.log_file.write(f"== ___________      .__               __________________  ________   =={NL}")
        self.log_file.write(f"== \__    ___/____  |  |   ____  _____\______   \______ \ \______ \  =={NL}")
        self.log_file.write(f"==   |    |  \__  \ |  |  /  _ \/  ___/|    |  _/|    |  \ |    |  \ =={NL}")
        self.log_file.write(f"==   |    |   / __ \|  |_(  <_> )___ \ |    |   \|    `   \|    `   \=={NL}")
        self.log_file.write(f"==   |____|  (____  /____/\____/____  >|______  /_______  /_______  /=={NL}")
        self.log_file.write(f"==                \/                \/        \/        \/        \/ =={NL}")
        self.log_file.write(DHR)
        self.log_file.write(f"============= SANTANDER GLOBAL TECH/QA - A taste of TALOS ============={NL}")

    def select_execution_title(self, execution_type):
        if execution_type == 'total':
            self.write_title_total_execution()
        elif execution_type == 'feature':
            self.write_title_feature_execution()

    def write_title_total_execution(self):
        self.log_file.write(DHR)
        self.log_file.write(f"==================  Result summary: execution total  =================={NL}")
        self.log_file.write(DHR)
        self.log_file.write(f'{NL}{NL}')

    def write_title_feature_execution(self):
        self.log_file.write(DHR)
        self.log_file.write(f"======================  Result summary: feature   ====================={NL}")
        self.log_file.write(DHR)
        self.log_file.write(f'{NL}{NL}')