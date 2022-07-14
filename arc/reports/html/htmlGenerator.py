import html
import json

from arc.reports.html.utils import (
    format_decimal, BASE_DIR, get_datetime_from_timestamp, get_duration, get_base64_image_by_path
)


class HtmlGenerator:
    features_failed = 0
    features_passed = 0
    features_passed_percent = "0"
    features_failed_percent = "0"
    total_features = 0

    total_scenarios = 0
    scenarios_passed = 0
    scenarios_failed = 0
    scenarios_passed_percent = "0"
    scenarios_failed_percent = "0"

    total_steps = 0
    steps_passed = 0
    steps_failed = 0

    start_time = 0
    end_time = 0

    css_styles = ""

    def __init__(self, features: []):
        """
            This object receives a list of features.
        :param features:
        :type Feature[]:
        """
        self.features = features
        self.total_features = len(features)
        self._calculate_features_values()
        self.css_styles = self.get_css_styles()

    @staticmethod
    def _create_file(file_name, text):
        """
            This method create the file given a file_name and write the text passed.
        :param file_name:
        :type file_name:
        :param text:
        :type text:
        :return:
        :rtype:
        """
        with open(f"{BASE_DIR}/output/reports/html/{file_name}.html", 'w') as file:
            file.write(text)

    @staticmethod
    def _read_from_file(file_name):
        """
            This method read and return the content from a HTML file in /arc/resources/html_templates.
        :param file_name:
        :type file_name:
        :return:
        :rtype:
        """
        with open(f'{BASE_DIR}/arc/resources/html_templates/{file_name}.html', 'r') as file:
            return file.read()

    @staticmethod
    def get_css_styles():
        """
            This method read the global.css file and return its content.
        :return:
        :rtype:
        """
        with open(f'{BASE_DIR}/arc/resources/talos_html_reports.css', 'r') as file:
            return file.read()

    def _calculate_features_values(self):
        """
            This method calculate the following values for the global file:
            - Start time of the execution
            - End time of the execution
            - Features passed
            - Features failed
            - Total scenarios
            - Scenarios passed
        :return:
        :rtype:
        """
        for idx, feature in enumerate(self.features):
            if len(self.features) == 1:
                self.start_time = get_datetime_from_timestamp(feature.start_time)
                self.end_time = get_datetime_from_timestamp(feature.end_time)
            elif idx == 0:
                self.start_time = get_datetime_from_timestamp(feature.start_time)
            elif idx == len(self.features)-1:
                self.end_time = get_datetime_from_timestamp(feature.end_time)

            if feature.status == "passed":
                self.features_passed += 1
            else:
                self.features_failed += 1

            self.total_scenarios += feature.total_scenarios
            self.scenarios_passed += feature.scenarios_passed
            self.scenarios_failed += feature.scenarios_failed

            self.total_steps += feature.total_steps

            self.steps_passed += feature.steps_passed
            self.steps_failed += feature.steps_failed

        self.scenarios_passed_percent = "0" if self.scenarios_passed == 0 else format_decimal(
            (self.scenarios_passed * 100) / self.total_scenarios)
        self.scenarios_failed_percent = "0" if self.scenarios_failed == 0 else format_decimal(
            (self.scenarios_failed * 100) / self.total_scenarios)

        self.features_passed_percent = "0" if self.features_passed == 0 else format_decimal(
            (self.features_passed * 100) / self.total_features
        )
        self.features_failed_percent = "0" if self.features_failed == 0 else format_decimal(
            (self.features_failed * 100) / self.total_features
        )

    def create_files(self):
        """
            This method starts the generation the global file, the features files and the scenarios files
        :return:
        :rtype:
        """
        self._create_global_file()
        for feature in self.features:
            self._create_feature_file(feature)
            for scenario in feature.scenarios:
                self._create_scenario_file(scenario)

    def _create_global_file(self):
        """
            This method create the global file.
            Its map the data to replace in the global template and create the new file.
        :return:
        :rtype:
        """
        data = {
            'style': self.css_styles,
            'features_count': str(self.total_features),
            'feature_progress_passed': self.features_passed_percent,
            'feature_progress_failed': self.features_failed_percent,
            'scenarios_count': str(self.total_scenarios),
            'scenarios_progress_passed': self.scenarios_passed_percent,
            'scenarios_progress_failed': self.scenarios_failed_percent,
            'global_features_overview': self._generate_html_table(self.features),
            'run_info': self._get_global_run_info()
        }
        text = self._read_from_file("global")
        text = self.replace_text(text, data)
        self._create_file("global", text)

    def _create_feature_file(self, feature):
        """
            This method create the feature file given a feature object.
            Its map the data to replace in the feature template and create the new file.
        :param feature:
        :type feature:
        :return:
        :rtype:
        """
        data = {
            'style': self.css_styles,
            'feature_name': feature.name,
            'scenarios_count': str(feature.total_scenarios),
            'scenario_progress_passed': feature.scenarios_passed_percent,
            'scenario_progress_failed': feature.scenarios_failed_percent,
            'steps_count': str(feature.total_steps),
            'steps_progress_passed': feature.steps_passed_percent,
            'steps_progress_failed': feature.steps_failed_percent,
            'steps_progress_skipped': feature.steps_skipped_percent,
            'feature_scenarios_overview': self._generate_html_table(feature.scenarios),
            'run_info': self._get_feature_run_info(feature)
        }
        text = self._read_from_file("feature")
        text = self.replace_text(text, data)
        self._create_file(f"feature_{feature.name}", text)

    def _create_scenario_file(self, scenario):
        """
            This method create the scenario file given a scenario object.
            Its map the data to replace in the scenario template and create the new file.
        :param scenario:
        :type scenario:
        :return:
        :rtype:
        """
        data = {
            'style': self.css_styles,
            'feature_name': scenario.feature_name,
            'scenario_name': scenario.name,
            'steps_count': str(scenario.total_steps),
            'steps_progress_passed': scenario.steps_passed_percent,
            'steps_progress_failed': scenario.steps_failed_percent,
            'steps_progress_skipped': scenario.steps_skipped_percent,
            'scenario_steps_overview': self.generate_html_steps_table(scenario.get_steps_data()),
            'scenario_steps_data': self._generate_html_steps_data(scenario),
            'run_info': self._get_scenario_run_info(scenario)

        }
        text = self._read_from_file("scenario")
        text = self.replace_text(text, data)
        self._create_file(f"scenario_{scenario.name}", text)
    
    @staticmethod
    def replace_text(text, replaces):
        """
            This method replace the text given a dictionary. The keys are the text to replace.
        :param text:
        :type text:
        :param replaces:
        :type replaces:
        :return:
        :rtype:
        """
        for replace, value in replaces.items():
            text = text.replace('{{'+replace+'}}', str(value))
        return text

    def _generate_html_steps_data(self, scenario):
        """
            This method generate the steps data given a scenario.
        :param scenario:
        :type scenario:
        :return:
        :rtype:
        """
        text = f""
        for index, step in enumerate(scenario.steps):
            text += f'''
                <div class="card">
                    <div class="card-header">
                        <h5 class="card-title" id=step-{index+1}>Step.{index+1} - {step.get("keyword")} {step.get("name")}</h5>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive step-data">
                            <table class="table">
                                <tr>
                                    <td>Location:</td>
                                    <td>{step.get("location")}</td>
                                </tr>
                                <tr>
                                    <td>Status:</td>
                                    <td class="text-capitalize">
                                        {step.get('result').get("status", '-') if step.get('result') else 'Skipped'}
                                    </td>
                                </tr>
                                <tr>
                                    <td>Duration:</td>
                                    <td>{get_duration(step.get('result').get('duration', 0)) if step.get('result') else '-'} </td>
                                </tr>
                                <tr>
                                    <td>Result:</td>
                                    <td>
                                        <code>
                                            {step.get('result').get("error_message", '-') if step.get('result') else '-'}
                                        </code>
                                    </td>
                                </tr>
                                {self._generate_step_api_data(step, index)}
                                {self._generate_api_evidence_extra_json(step, index)}
                                {self._api_evidence_info(step)}
                                {self._api_evidence_verify(step)}
                                {self._generate_steps_screenshots(step)}
                            </table>
                        </div>
                    </div>
                </div>
            '''
        return text

    @staticmethod
    def _generate_step_api_data(step:dict, index):
        """
            This method generate the api step data given a step dictionary and an index
        :param step:
        :type step:
        :param index:
        :type index:
        :return:
        :rtype:
        """
        text = f""
        if step.get('request'):
            step_request = step.get('request')
            header = step_request.get("headers") if step_request.get("headers") is not None else 'No headers'
            body = step_request.get("body") if step_request.get("body")[0] is not None else 'No body'
            text += f'''
                <tr>
                    <td>Request info</td>
                    <td>
                        <a class="collapse-request collapsed" data-toggle="collapse"
                            href="#request_{index}" role="button" aria-expanded="false"
                            aria-controls="request_{index}">
                            Show request data
                        </a>
                        <div class="collapse" id="request_{index}">
                            <p>Endpoint: {step_request.get("url")}</p>
                            <p>Headers: <pre>{json.dumps(header, indent=4).strip()}</pre></p>
                            <p>Body: <pre>{json.dumps(body, indent=4).strip()}</pre></p>
                        </div>
                    </td>
                </tr>
            '''
        if step.get('response_content') is not None:
            text += f'''
                <tr>
                    <td>
                        Response info:          
                    </td>
                    <td>
                        <a class="collapse-response collapsed" data-toggle="collapse"
                            href="#response_{index}" role="button" aria-expanded="false"
                            aria-controls="response_{index}">
                            Show response data
                        </a>
                        <div class="collapse" id="response_{index}">
                            <pre>{step.get('response_content', '-')}</pre> 
                        </div>                    
                    </td>
                </tr>
            '''
        return text

    @staticmethod
    def _generate_api_evidence_extra_json(step: dict, index):
        """
            This method generate the evidence extra json data given a step dictionary and an index
        :param step:
        :type step:
        :param index:
        :type index:
        :return:
        :rtype:
        """
        text = ""
        if step.get('api_evidence_extra_json') and len(step.get('api_evidence_extra_json')) > 0:
            for evidence in step.get('api_evidence_extra_json', []):
                text += f'''
                    <tr>
                        <td>Extra evidence json: </td>
                        <td>
                            <a class="collapse-evidence-extra collapsed" data-toggle="collapse"
                                href="#evidence_extra_{index}" role="button" aria-expanded="false"
                                aria-controls="response_{index}">
                                Show evidence extra json
                            </a>
                            <div class="collapse" id="evidence_extra_{index}">
                                <pre>{json.dumps(evidence, indent=4)}</pre>
                            </div>
                        </td>
                    </tr>
                '''
        return text

    @staticmethod
    def _api_evidence_info(step: dict):
        """
            This method generates the api evidence info given a step dictionary.
        :param step:
        :type step:
        :return:
        :rtype:
        """
        text = ""
        if step.get('api_evidence_info') and len(step.get('api_evidence_info')) > 0:
            evidence = step.get('api_evidence_info')
            text += f'''
                <tr class="tr-dark">
                    <td colspan="2">Api evidence info: </td>
                </tr>
                <tr>
                    <td>Url: </td>
                    <td>{evidence['URL']}</td>
                </tr>
                <tr>
                    <td>Method: </td>
                    <td>{evidence['Method']}</td>
                </tr>
                <tr>
                    <td>Reason: </td>
                    <td>{evidence['Reason']}</td>
                </tr>
                <tr>
                    <td>Status Code: </td>
                    <td>{evidence['Status Code']}</td>
                </tr>
            '''
        return text

    @staticmethod
    def _api_evidence_verify(step: dict):
        """
            This method generates the api evidence verify given a step dictionary.
        :param step:
        :type step:
        :return:
        :rtype:
        """
        text = f""
        if step.get('api_evidence_verify', []) and len(step.get('api_evidence_verify')) > 0:
            for evidence in step.get('api_evidence_verify', []):
                text += f'''
                    <tr class="tr-dark">
                        <td colspan="2">Api evidence verify: </td>
                    </tr>
                '''
                for key, value in evidence.items():
                    if value is not None:
                        text += f'''
                            <tr>
                                <td>{key.replace('_', ' ')}: </td>
                                <td>{html.escape(value) if isinstance(value, str) else value}</td>
                            </tr>
                        '''
        return text

    @staticmethod
    def _generate_steps_screenshots(step: dict):
        """
            This method generate the thumbnails given a step dictionary in case there are screenshots.
        :param step:
        :type step:
        :return:
        :rtype:
        """
        text = ""
        if step.get("screenshots") is not None and len(step.get("screenshots")):
            text += f'''
                <tr>
                <td>Screenshots</td>
                <td class="screenshots-grid">
            '''
            for screenshot in step.get("screenshots"):
                text += f'''
                    
                        <div class="thumbnail-container">
                            <a href="" data-fancybox>
                                <img class="img-thumbnail" src="data:image/png;base64, {get_base64_image_by_path(screenshot)}">
                            </a>
                        </div>
                '''
            text += f'''
                    </td>
                </tr>
            '''
        return text

    @staticmethod
    def _generate_html_table(items: list):
        """
            This step generate an html table for items.
            Items can be features or scenarios.
            Param items must be a list of steps or scenarios
        :param items:
        :type items:
        :return:
        :rtype:
        """
        text = ""
        for item in items:
            text += "<tr>"
            for data in item.get_data().values():
                text += f"<td>{data}</td>"
            text += "</tr>"
        return text

    @staticmethod
    def generate_html_steps_table(items: list):
        """
            This method generate a html table with the steps data.
            Param items must be a list of steps.
        :param items:
        :type items:
        :return:
        :rtype:
        """
        text = ""
        for index, step in enumerate(items):
            text += f'''
                <tr>
                    <td><a href="#step-{index+1}">{index+1} - {step.get('name')}</a></td>
                    <td>{step.get('status')}</td>
                    <td>{step.get('start_time')}</td>
                    <td>{step.get('end_time')}</td>
                    <td>{step.get('duration')}</td>
                </tr>
            '''
        return text

    def _get_global_run_info(self):
        """
            This method return a html table for global run info.
        :return:
        :rtype:
        """
        return f'''
            <tr>
                <td>Total features: </td>
                <td>{self.total_features}</td>
            </tr>
            <tr>
                <td>Total scenarios:</td>
                <td>{self.total_scenarios}</td>
            </tr>
            <tr>
                <td>Scenarios passed:</td>
                <td>{self.scenarios_passed}</td>
            </tr>
            <tr>
                <td>Scenarios failed:</td>
                <td>{self.scenarios_failed}</td>
            </tr>
            <tr>
                <td>Total steps: </td>
                <td>{self.total_steps}</td>
            </tr>
            <tr>
                <td>Steps passed:</td>
                <td>{self.steps_passed}</td>
            </tr>
            <tr>
                <td>Steps failed:</td>
                <td>{self.steps_failed}</td>
            </tr>
            <tr>
                <td>Execution start time:</td>
                <td>{self.start_time}</td>
            </tr>
            <tr>
                <td>Execution end time:</td>
                <td>{self.end_time}</td>
            </tr>
        '''

    def _get_feature_run_info(self, feature):
        """
            This method return a html table for feature run info given a feature object
        :param feature:
        :type feature:
        :return:
        :rtype:
        """
        return f'''
            <tr>
                <td>Operating system</td>
                <td>{feature.operating_system}</td>
            </tr>
            <tr>
                <td>Driver</td>
                <td>{feature.driver}</td>
            </tr>
            <tr>
                <td>Total scenarios:</td>
                <td>{feature.total_scenarios}</td>
            </tr>
            <tr>
                <td>Total steps:</td>
                <td>{feature.total_steps}</td>
            </tr>
            <tr>
                <td>Passed steps:</td>
                <td>{feature.steps_passed}</td>
            </tr>
            <tr>
                <td>Failed steps:</td>
                <td>{feature.steps_failed}</td>
            </tr>
            <tr>
                <td>Skipped steps:</td>
                <td>{feature.steps_skipped}</td>
            </tr>
            <tr>
                <td>Execution start time:</td>
                <td>{get_datetime_from_timestamp(feature.start_time)}</td>
            </tr>
            <tr>
                <td>Execution end time: </td>
                <td>{get_datetime_from_timestamp(feature.end_time)}</td>
            </tr>
            <tr>
                <td>Duration: </td>
                <td>{feature.total_duration}</td>
            </tr>
        '''

    def _get_scenario_run_info(self, scenario):
        """
            This method return a html table for scenario run info given a scenario object
        :param scenario:
        :type scenario:
        :return:
        :rtype:
        """
        return f'''
            <tr>
                <td>Total steps: </td>
                <td>{scenario.total_steps}</td>
            </tr>
            <tr>
                <td>Passed steps:</td>
                <td>{scenario.passed_steps}</td>
            </tr>
            <tr>
                <td>Failed steps:</td>
                <td>{scenario.failed_steps}</td>
            </tr>
            <tr>
                <td>Skipped steps:</td>
                <td>{scenario.skipped_steps}</td>
            </tr>
            <tr>
                <td>Execution start time: </td>
                <td>{get_datetime_from_timestamp(scenario.start_time)}</td>
            </tr>
            <tr>
                <td>Execution end time: </td>
                <td>{get_datetime_from_timestamp(scenario.end_time)}</td>
            </tr>
            <tr>
                <td>Total duration: </td>
                <td>{scenario.total_duration}</td>
            </tr>
        '''
