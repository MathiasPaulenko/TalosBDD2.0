import os
import time
import requests
import urllib3
from datetime import datetime

from settings import settings

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

LOG_PATH = os.path.join(settings.OUTPUT_PATH, 'logs' + os.sep + 'execution_log.txt')
HTML_PATH = os.path.join(settings.OUTPUT_PATH, 'reports' + os.sep + 'html' + os.sep)


class Jira:
    scenarios_list = []
    html_list = []

    def __init__(self):
        self.username = settings.PYTALOS_JIRA['username']
        self.password = settings.PYTALOS_JIRA['password']
        self.base_url = settings.PYTALOS_JIRA['base_url']

    def set_scenario(self, scenario, doc_path):
        tags = self._get_jira_tag(scenario.tags)
        for tag in tags:
            feature_name = scenario.feature.name
            scenario_name = scenario.name
            steps = self._format_scenario_step(scenario.steps)
            description = self._format_scenario_data(scenario.description)
            scenario_result = str(scenario.status)
            dictionary = {tag: {
                'feature_name': feature_name,
                'feature_filename': scenario.feature.filename,
                'scenario_name': scenario_name,
                'steps': steps,
                'description': description,
                'doc_path': doc_path,
                'scenario_result': scenario_result,
                'date': str(datetime.today().strftime('%d-%m-%Y')),
                'duration': scenario.duration
            }}
            self.scenarios_list.append(dictionary)

    def post_to_jira(self):
        if settings.PYTALOS_JIRA['report']['upload_doc_evidence']:
            self._add_issue_evidence()
        if settings.PYTALOS_JIRA['report']['comment_execution']:
            self._add_total_comment_in_issue()
        if settings.PYTALOS_JIRA['report']['comment_scenarios']:
            self._add_comment_in_issue()
        self._add_issue_extra_attach()

    @staticmethod
    def _get_jira_tag(tags):
        final_tags = []
        for tag in tags:
            if str(tag).startswith('JIRA-'):
                final_tags.append(tag)
        return final_tags

    @staticmethod
    def _format_scenario_data(data):
        return "\n".join(str(x) for x in data)

    @staticmethod
    def _format_scenario_step(data):
        steps = "\n".join(str(x) for x in data)
        steps = steps \
            .replace('given', '--- {color:purple}*Given*{color}') \
            .replace('when', '--- {color:orange}*When*{color}') \
            .replace('then', '--- {color:violet}*Then*{color}') \
            .replace('\"', "")
        return steps

    def _add_comment_in_issue(self):
        for scenario in self.scenarios_list:
            for key in scenario.keys():
                scenario_data = scenario[key]
                api = f'{self.base_url}/rest/api/2/issue/{self._parse_tag(key)}/comment'
                headers = {'Content-Type': 'application/json'}
                comment = self._parse_comment(scenario_data)
                body = {'body': comment}
                requests.post(api, auth=(self.username, self.password), json=body, headers=headers, verify=False)

    def _add_total_comment_in_issue(self):
        scenario_dict = self._join_scenarios()
        for scenario_tag in scenario_dict:
            comment = self._parse_total_comment(scenario_dict[scenario_tag])
            api = f'{self.base_url}/rest/api/2/issue/{self._parse_tag(scenario_tag)}/comment'
            headers = {'Content-Type': 'application/json'}
            body = {'body': comment}
            requests.post(api, auth=(self.username, self.password), json=body, headers=headers, verify=False)

    def _add_issue_evidence(self):
        for scenario in self.scenarios_list:
            for key in scenario.keys():
                scenario_data = scenario[key]
                self._delete_attachment(str(scenario_data['doc_path']).split('\\')[-1])
                api = f'{self.base_url}/rest/api/2/issue/{self._parse_tag(key)}/attachments'
                headers = {"X-Atlassian-Token": "nocheck"}
                doc_path = scenario_data['doc_path']
                files = [('file', open(doc_path, 'rb'))]
                requests.post(api, auth=(self.username, self.password), files=files, headers=headers, verify=False)

    def _add_issue_extra_attach(self):
        headers = {"X-Atlassian-Token": "nocheck"}

        # update execution txt log
        if settings.PYTALOS_REPORTS['generate_txt']:
            if settings.PYTALOS_JIRA['report']['upload_txt_evidence']:
                scenario_dict = self._join_scenarios()
                if os.path.isfile(LOG_PATH):
                    for scenario_tag in scenario_dict:
                        self._delete_attachment(str(LOG_PATH).split('\\')[-1])
                        api = f'{self.base_url}/rest/api/2/issue/{self._parse_tag(scenario_tag)}/attachments'
                        files = [('file', open(LOG_PATH, 'rb'))]
                        requests.post(api, auth=(self.username, self.password), files=files, headers=headers,
                                      verify=False)

        # html report
        if settings.PYTALOS_REPORTS['generate_html']:
            if settings.PYTALOS_JIRA['report']['upload_html_evidence']:
                scenario_dict = self._join_scenarios()
                if self.html_list:
                    for tags in scenario_dict:
                        for scenario in scenario_dict[tags]:
                            html_filename = self._format_feature_filename_to_html(scenario['feature_filename'])
                            html_path = os.path.join(HTML_PATH, html_filename)
                            self._delete_attachment(html_filename)
                            api = f'{self.base_url}/rest/api/2/issue/{self._parse_tag(tags)}/attachments'
                            files = [('file', open(html_path, 'rb'))]
                            requests.post(api, auth=(self.username, self.password), files=files, headers=headers,
                                          verify=False)

    @staticmethod
    def _format_feature_filename_to_html(feature_filename):
        feature_filename = str(feature_filename).replace(".feature", ".html")
        feature_filename = str(feature_filename).replace("/", ".")
        final_filename = f'TESTS-{feature_filename}'
        return final_filename

    def _get_attachment_data(self):
        headers = {"X-Atlassian-Token": "nocheck"}
        scenario_dict = self._join_scenarios()
        current_attachments = []
        for scenario_tag in scenario_dict:
            tag = self._parse_tag(scenario_tag)
            api = f'{self.base_url}/rest/api/2/issue/{self._parse_tag(tag)}'
            response = requests.get(api, auth=(self.username, self.password), headers=headers, verify=False)
            issues_attachments = self._get_issue_id_name_attachment(response)
            current_attachments.append(issues_attachments)

        return current_attachments

    @staticmethod
    def _get_issue_id_name_attachment(response):
        response_json = response.json()
        attachments = response_json['fields']['attachment']
        current_attachment = []
        for attach in attachments:
            current_attachment.append({
                'id': attach['id'],
                'name': attach['filename']
            })
        return current_attachment

    def _delete_attachment(self, attachment_to_delete):
        current_attachments = self._get_attachment_data()
        attach_id = ""
        for attachments in current_attachments:
            for attachment in attachments:
                if attachment['name'] == attachment_to_delete:
                    attach_id = attachment['id']

        if attach_id != "":
            headers = {"X-Atlassian-Token": "nocheck"}
            api = f'{self.base_url}/rest/api/2/attachment/{attach_id}'
            requests.delete(api, auth=(self.username, self.password), headers=headers, verify=False)

    @staticmethod
    def _parse_tag(tag):
        return str(tag).replace('JIRA-', '')

    @staticmethod
    def _parse_comment(scenario_data):
        feature_name = scenario_data['feature_name']
        description = scenario_data['description']
        scenario_name = scenario_data['scenario_name']
        steps = scenario_data['steps'].replace('<', '').replace('>', '')
        evidence = str(scenario_data['doc_path']).split('\\')[-1]
        result = scenario_data['scenario_result'].split('.')[1].upper()
        date = scenario_data['date']
        coe_text = '--- CoE Testing Automation --- Automation Toolkit'

        if result == 'PASSED':
            result = '{color:green}*' + result + '*{color}'
        elif result == 'FAILED':
            result = '{color:red}*' + result + '*{color}'
        else:
            result = '{color:blue}*' + result + '*{color}'

        ln = '\n'
        strong = '*'
        sep = '=' * 60
        return f'h2. Scenario Test: {scenario_name}{ln}' \
               f'{strong}Feature Name:{strong} {feature_name}{ln}' \
               f'{strong}Execution date:{strong} {date}{ln}' \
               f'{strong}Scenario Description:{strong}{ln}{description}' \
               f'{ln}{strong}{sep}{strong}{ln}' \
               f'{steps}' \
               f'{ln}{strong}{sep}{strong}{ln}' \
               f'{strong}Scenario Result:{strong} {result}{ln}' \
               f'{strong}Attached evidence:{strong} [^{evidence}]{ln}{ln}{ln}{ln}' \
               f'h6. Report created programmatically by: {strong}TalosBDD Automation Framework{strong} {coe_text}'

    def _parse_total_comment(self, scenarios_list):
        execution_title = "Automated Test Execution Summary."
        execution_result = self._get_scenario_result(scenarios_list)
        execution_date = str(datetime.today().strftime('%d-%m-%Y'))
        tc_title = "Test Case Executed:"
        tcs_info = self._get_total_scenario_name(scenarios_list)
        execution_info_title = "Execution Information:"
        total_scenario = len(scenarios_list)
        scenario_passed = self._count_scenario_result(scenarios_list)['passed']
        scenario_failed = self._count_scenario_result(scenarios_list)['failed']
        scenario_skipped = self._count_scenario_result(scenarios_list)['skipped']
        scenario_success_rate = f"{(scenario_passed * 100) / total_scenario}"
        execution_duration = self._get_total_duration(scenarios_list)
        coe_text = '--- CoE Testing Automation --- Automation Toolkit'
        ln = '\n'
        strong = '*'
        sep = '-' * 80

        return f'h1. {execution_title}{ln}{ln}{ln}{ln}' \
               f'* {strong}Execution Result:{strong} {execution_result}{ln}' \
               f'* {strong}Execution Date:{strong} {execution_date}{ln}{ln}{ln}' \
               f'h3. {strong}{tc_title}{strong}{ln}' \
               f'{strong}{sep}{strong}{ln}' \
               f'{tcs_info}{ln}' \
               f'{ln}{strong}{sep}{strong}{ln}{ln}{ln}' \
               f'h3.{strong}{execution_info_title}{strong}{ln}' \
               f'{strong}{sep}{strong}{ln}' \
               f'* {strong}Total Executed Scenario:{strong} {total_scenario}{ln}' \
               f'* {strong}Passed Scenario:{strong} {scenario_passed}{ln}' \
               f'* {strong}Failed Scenario:{strong} {scenario_failed}{ln}' \
               f'* {strong}Skipped Scenario:{strong} {scenario_skipped}{ln}' \
               f'* {strong}Scenario Success Rate:{strong} {scenario_success_rate}%{ln}' \
               f'* {strong}Execution Duration:{strong} {execution_duration}{ln}' \
               f'{ln}{strong}{sep}{strong}{ln}{ln}{ln}{ln}' \
               f'h6. Report created programmatically by: {strong}TalosBDD Automation Framework{strong} {coe_text}'

    def _get_total_duration(self, scenario_list):
        total_duration = 0
        for scenario_data in scenario_list:
            total_duration += scenario_data['duration']

        return self._format_duration(total_duration)

    def _get_total_scenario_name(self, scenario_list):
        scenario_name = []
        slash = "\\"
        for scenario_data in scenario_list:
            emoticon = self._get_result_emoticon(self._format_result(scenario_data["scenario_result"]))
            attachment = str(scenario_data["doc_path"]).split(slash)[-1]
            scenario_info = f'# {emoticon} --- {scenario_data["feature_name"]} ' \
                            f'--- [{scenario_data["scenario_name"]}|^{attachment}] ' \
                            f'--- {self._format_duration(scenario_data["duration"])} ' \
                            f'--- {self._format_result(scenario_data["scenario_result"])}'
            scenario_name.append(scenario_info)

        return "\n".join(str(x) for x in scenario_name)

    @staticmethod
    def _get_result_emoticon(result):
        if 'PASSED' in result:
            return '(/)'
        elif 'FAILED' in result:
            return '(x)'
        else:
            return '(!)'

    @staticmethod
    def _format_result(result):
        result = result.split('.')[1].upper()
        if result == 'PASSED':
            return '{color:green}*' + result + '*{color}'
        elif result == 'FAILED':
            return '{color:red}*' + result + '*{color}'
        else:
            return '{color:blue}*' + result + '*{color}'

    @staticmethod
    def _get_scenario_result(scenario_list):
        result_list = []
        for scenario_data in scenario_list:
            result = scenario_data['scenario_result'].split('.')[1].upper()
            result_list.append(result)

        if 'FAILED' in result_list and 'SKIPPED' not in result_list:
            return '{color:red}*FAILED*{color} :('
        elif 'FAILED' not in result_list and 'SKIPPED' not in result_list:
            return '{color:green}*PASSED*{color} :D'
        else:
            return '{color:blue}*SKIPPED*{color} :P'

    def _count_scenario_result(self, scenario_list):
        passed = 0
        failed = 0
        skipped = 0
        for scenario_data in scenario_list:
            result = self._format_result(scenario_data["scenario_result"])
            if 'PASSED' in result:
                passed += 1
            elif 'FAILED' in result:
                failed += 1
            else:
                skipped += 1

        return {
            'passed': passed,
            'failed': failed,
            'skipped': skipped,
            'total': passed + failed + skipped
        }

    def _join_scenarios(self):
        final_dict = {}
        for scenario_dict in self.scenarios_list:
            for tag in scenario_dict.keys():
                if tag not in final_dict.keys():
                    final_dict.update({tag: []})
                final_dict[tag].append(scenario_dict[tag])
        return final_dict

    @staticmethod
    def _format_duration(duration):
        return f"{time.strftime('%H:%M:%S', time.gmtime(duration))}"
