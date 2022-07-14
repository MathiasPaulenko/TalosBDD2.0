import json as j
import os
import datetime
import re

from arc.reports.csv_formmater import CSVFormatter
from arc.reports.html.utils import BASE_DIR
from arc.settings import settings

JSON_PATH = os.path.join(settings.OUTPUT_PATH, 'json/input/')


class GenerateJson:
    alm = {}
    json_name = ''
    scenario_name = ''
    csv: CSVFormatter
    csv_data = {}
    csv_heading = []
    step_controller = []
    step_dict = {}
    step_cont = 0
    cd = datetime.datetime.now()

    def __init__(self, scenario):
        self.csv = CSVFormatter()
        self.set_csv_data_config(scenario)
        self.set_alm_part()
        self.set_tc_part()
        self.set_ts_part(scenario)
        self.step_controller = []
        self.step_dict = {}

    def generate_json_after_scenario(self, scenario, doc_path, generate_html_report):
        self.set_run_part(scenario, doc_path, generate_html_report)
        self.finish_json()

    def generate_json_after_step(self, step):
        self.set_step(step)

    def set_names(self, scenario):
        self.set_feature_name(scenario)
        self.set_scenario_name(scenario)

    def set_feature_name(self, scenario):
        self.json_name = self.csv.format_feature_name(scenario)
        aux = "-" + re.sub('[-#%<>@ ]', "", scenario.name)
        aux = re.sub('[.]', "-", aux)
        self.json_name += aux + '_' + str(self.cd.hour) + '_' + str(self.cd.minute) \
                          + '_' + str(self.cd.second) + '-' + str(self.cd.day) \
                          + '_' + str(self.cd.month) + '_' + str(self.cd.year)
        self.json_name.replace(" ", "-")

    def set_scenario_name(self, scenario):
        self.csv.set_scenario_data(scenario)
        self.scenario_name = self.csv.tc_scenario_name

    def set_csv_data_config(self, scenario):
        self.set_names(scenario)
        self.csv_data = self.csv.get_final_data()
        self.step_cont = 0

    def set_alm_part(self):
        self.alm['alm-access'] = [self.csv_data[1]]

    def set_tc_part(self):
        self.alm['test-case'] = [self.csv_data[2]]

    def set_ts_part(self, scenario):
        self.alm['test-set'] = [self.csv_data[3]]

    def set_run_part(self, scenario, doc_path, generate_html_report):
        if str(scenario.status) == 'Status.passed':
            result = "Passed"
        elif str(scenario.status) == "Status.failed":
            result = "Failed"
        else:
            result = "Skipped"
        self.alm['run'] = []
        self.alm['run'].append({
            "run-exec-date": str(self.cd.day) + "/" + str(self.cd.month) + "/" + str(self.cd.year),
            "run-exec-time": str(self.cd.hour) + ":" + str(self.cd.minute) + ":" + str(self.cd.second),
            "run-status": result,
            "run-duration": str(round(scenario.duration, 2)),
            "run-attach-1": doc_path.__str__(),
        })

        if generate_html_report:
            self.alm['run'][0]['run-attach-2'] = f"{BASE_DIR}/output/reports/html/scenario_{scenario.name}.html"

    def set_step(self, step):
        date_time = datetime.datetime.now()
        self.step_cont += 1
        if str(step.status) == 'Status.passed':
            if step.obtained_result_passed:
                obt_result = str(step.obtained_result_passed).replace("'", "")
            else:
                obt_result = "Operation with correct result"
            result = "Passed"
        elif str(step.status) == "Status.failed":
            if step.obtained_result_failed:
                obt_result = str(step.obtained_result_failed).replace("'", "")
            else:
                obt_result = "Operation with incorrect result"
            result = "Failed"
        else:
            if step.obtained_result_skipped:
                obt_result = str(step.obtained_result_skipped).replace("'", "")
            else:
                obt_result = "Operation skipped"
            result = "No Run"

        if step.result_expected:
            result_expected = str(step.result_expected).replace("'", "")
        else:
            result_expected = str(step.name).replace("<", "").replace(">", "")

        step_description = str(step.name).replace("<", "").replace(">", "").replace("'", "").replace("\"", "")

        self.step_dict = {
            "step-number": "Step " + str(self.step_cont),
            "step-descrip": str(step.keyword) + " " + str(step_description),
            "step-exp-res": str(result_expected),
            "step-obt-res": obt_result,
            "step-exec-stat": result,
            "step-exec-date": str(date_time.day) + "/" + str(date_time.month) + "/" + str(date_time.year),
            "step-exec-time": str(round(step.duration, 2))
        }

        self.step_controller.append(self.step_dict)
        self.alm['steps'] = self.step_controller

    def finish_json(self):
        self.json_name = self.json_name.replace("/", "-")
        path = os.path.join(JSON_PATH, self.json_name + '.json')
        with open(path, 'w', encoding='utf-8') as outfile:
            j.dump(self.alm, outfile, ensure_ascii=False)
