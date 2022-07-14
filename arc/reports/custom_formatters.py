import base64
import datetime
import json
import platform

from behave.formatter.base import Formatter
from behave.model_core import Status

from arc.core.behave.env_utils import generate_html_reports
from settings import settings
from urllib3.packages import six


class CustomJSONFormatter(Formatter):
    """
        This is a custom json formatter to generate the talos_report.json
    """
    name = "json"
    description = "JSON dump of test run"
    dumps_kwargs = {}
    split_text_into_lines = True   # EXPERIMENT for better readability.

    json_number_types = six.integer_types + (float,)
    json_scalar_types = json_number_types + (six.text_type, bool, type(None))

    def __init__(self, stream_opener, config):
        super().__init__(stream_opener, config)
        # -- ENSURE: Output stream is open.
        self.stream = self.open()
        self.feature_count = 0
        self.current_feature = None
        self.current_feature_data = None
        self.current_scenario = None
        self._step_index = 0

    def reset(self):
        self.current_feature = None
        self.current_feature_data = None
        self.current_scenario = None
        self._step_index = 0

    # -- FORMATTER API:
    def uri(self, uri):
        pass

    def feature(self, feature):
        """
            This method generate feature data BEFORE executing it.
            So there is no way to add new data using this method.
        :param feature:
        :type feature:
        :return:
        :rtype:
        """
        self.reset()
        self.current_feature = feature
        self.current_feature_data = {
            "keyword": feature.keyword,
            "name": feature.name,
            "tags": list(feature.tags),
            "location": six.text_type(feature.location),
            "status": None,     # Not known before feature run.
        }
        element = self.current_feature_data
        if feature.description:
            element["description"] = feature.description

    def background(self, background):
        """
            This method generate background data BEFORE executing it.
            So there is no way to add new data using this method.
        :param background:
        :type background:
        :return:
        :rtype:
        """
        element = self.add_feature_element({
            "type": "background",
            "keyword": background.keyword,
            "name": background.name,
            "location": six.text_type(background.location),
            "steps": [],
        })
        if background.name:
            element["name"] = background.name
        self._step_index = 0

        # -- ADD BACKGROUND STEPS: Support *.feature file regeneration.
        for step_ in background.steps:
            self.step(step_)

    def scenario(self, scenario):
        """
            This method generate scenario data BEFORE executing it.
            So there is no way to add new data using this method.
        :param scenario:
        :type scenario:
        :return:
        :rtype:
        """
        self.finish_current_scenario()
        self.current_scenario = scenario

        element = self.add_feature_element({
            "type": "scenario",
            "keyword": scenario.keyword,
            "name": scenario.name,
            "tags": scenario.tags,
            "location": six.text_type(scenario.location),
            "steps": [],
            "status": None,
        })
        if scenario.description:
            element["description"] = scenario.description
        self._step_index = 0

    @classmethod
    def make_table(cls, table):
        table_data = {
            "headings": table.headings,
            "rows": [list(row) for row in table.rows]
        }
        return table_data

    def step(self, step):
        s = {
            "keyword": step.keyword,
            "step_type": step.step_type,
            "name": step.name,
            "location": six.text_type(step.location),
        }

        if step.text:
            text = step.text
            if self.split_text_into_lines and "\n" in text:
                text = text.splitlines()
            s["text"] = text
        if step.table:
            s["table"] = self.make_table(step.table)
        element = self.current_feature_element
        element["steps"].append(s)

    def match(self, match):
        args = []
        for argument in match.arguments:
            argument_value = argument.value
            if not isinstance(argument_value, self.json_scalar_types):
                # -- OOPS: Avoid invalid JSON format w/ custom types.
                # Use raw string (original) instead.
                argument_value = argument.original
            assert isinstance(argument_value, self.json_scalar_types)
            arg = {
                "value": argument_value,
            }
            if argument.name:
                arg["name"] = argument.name
            if argument.original != argument_value:
                # -- REDUNDANT DATA COMPRESSION: Suppress for strings.
                arg["original"] = argument.original
            args.append(arg)

        match_data = {
            "location": six.text_type(match.location) or "",
            "arguments": args,
        }
        if match.location:
            # -- NOTE: match.location=None occurs for undefined steps.
            steps = self.current_feature_element["steps"]
            steps[self._step_index]["match"] = match_data

    def result(self, step):
        """
            When a step end, the result data is generated here.
        :param step:
        :type step:
        :return:
        :rtype:
        """
        steps = self.current_feature_element["steps"]
        steps[self._step_index]["result"] = {
            "status": step.status.name,
            "duration": step.duration,
        }

        # Extra data.
        steps[self._step_index]['start_time'] = step.start_time
        steps[self._step_index]['end_time'] = step.end_time
        steps[self._step_index]["screenshots"] = step.screenshots
        steps[self._step_index]["request"] = step.request
        steps[self._step_index]["response_content"] = step.response_content
        #
        steps[self._step_index]["api_evidence_extra_json"] = step.api_evidence_extra_json
        steps[self._step_index]["api_evidence_info"] = step.api_evidence_info
        steps[self._step_index]["api_evidence_verify"] = step.api_evidence_verify

        if step.error_message and step.status == Status.failed:
            # -- OPTIONAL: Provided for failed steps.
            # error_message = step.error_message
            # if self.split_text_into_lines and "\n" in error_message:
            #     error_message = error_message.splitlines()
            result_element = steps[self._step_index]["result"]
            result_element["error_message"] = step.exception.__str__()
        self._step_index += 1

    def embedding(self, mime_type, data):
        step = self.current_feature_element["steps"][-1]
        step["embeddings"].append({
            "mime_type": mime_type,
            "data": base64.b64encode(data).replace("\n", ""),
        })

    def eof(self):
        """
        This method writes the feature data when the feature execution ended.
        End of feature
        """
        if not self.current_feature_data:
            return

        self.add_scenario_data()
        self.add_feature_data()
        # -- NORMAL CASE: Write collected data of current feature.
        self.finish_current_scenario()
        self.update_status_data()

        if self.feature_count == 0:
            # -- FIRST FEATURE:
            self.write_json_header()
        else:
            # -- NEXT FEATURE:
            self.write_json_feature_separator()

        self.write_json_feature(self.current_feature_data)
        self.reset()
        self.feature_count += 1

    def close(self):
        """
            Close the stream.
        :return:
        :rtype:
        """
        if self.feature_count == 0:
            # -- FIRST FEATURE: Corner case when no features are provided.
            self.write_json_header()
        self.write_json_footer()
        self.close_stream()

        if settings.PYTALOS_REPORTS.get('generate_html', False):
            generate_html_reports()

    # -- JSON-DATA COLLECTION:
    def add_feature_element(self, element):
        assert self.current_feature_data is not None
        if "elements" not in self.current_feature_data:
            self.current_feature_data["elements"] = []
        self.current_feature_data["elements"].append(element)
        return element

    @property
    def current_feature_element(self):
        assert self.current_feature_data is not None
        return self.current_feature_data["elements"][-1]

    def update_status_data(self):
        assert self.current_feature
        assert self.current_feature_data
        self.current_feature_data["status"] = self.current_feature.status.name

    def finish_current_scenario(self):
        if self.current_scenario:
            status_name = self.current_scenario.status.name
            self.current_feature_element["status"] = status_name

    # -- JSON-WRITER:
    def write_json_header(self):
        self.stream.write("{\n \"features\":[")

    def write_json_footer(self):
        """
            This method end the features list and add the global data.
        :return:
        :rtype:
        """
        self.stream.write("],")
        self.stream.write(self.add_global_data())
        self.stream.write("\n}\n")

    def write_json_feature(self, feature_data):
        """
            This method write the feature data to the json file
        :param feature_data:
        :type feature_data:
        :return:
        :rtype:
        """
        self.stream.write(json.dumps(feature_data, **self.dumps_kwargs))
        self.stream.flush()

    def write_json_feature_separator(self):
        self.stream.write(",\n\n")

    def add_scenario_data(self):
        """
            This method add scenario data from the current_feature to the current_feature_data.
        :return:
        :rtype:
        """
        scenarios_feature_data = [element for element in self.current_feature_data['elements']
                                  if element.get("status") != "skipped" and
                                  element.get("type") in ['scenario', 'scenario_outline']]

        scenarios_list = []

        for idx, scenario in enumerate(self.current_feature.scenarios):
            if scenario.type == "scenario":
                if scenario.status != "skipped":
                    scenarios_feature_data[idx] = update_feature_scenario_data(
                        scenarios_feature_data[idx], scenario)
            elif scenario.type == "scenario_outline":
                scenarios_list += [_scenario for _scenario in scenario.scenarios]

        if len(scenarios_list):
            for idx, scenario in enumerate(scenarios_list):
                if scenario.status != "skipped":
                    scenarios_feature_data[idx] = update_feature_scenario_data(
                        scenarios_feature_data[idx], scenario)

    def add_feature_data(self):
        """
            This method add feature data from the current_feature to the current_feature_data
        :return:
        :rtype:
        """
        self.current_feature_data['total_scenarios'] = self.current_feature.total_scenarios
        self.current_feature_data['passed_scenarios'] = self.current_feature.passed_scenarios
        self.current_feature_data['failed_scenarios'] = self.current_feature.failed_scenarios
        self.current_feature_data['scenarios_passed_percent'] = self.current_feature.scenarios_passed_percent
        self.current_feature_data['scenarios_failed_percent'] = self.current_feature.scenarios_failed_percent
        self.current_feature_data['total_steps'] = self.current_feature.total_steps
        self.current_feature_data['steps_passed'] = self.current_feature.steps_passed
        self.current_feature_data['steps_failed'] = self.current_feature.steps_failed
        self.current_feature_data['steps_skipped'] = self.current_feature.steps_skipped
        self.current_feature_data['steps_passed_percent'] = self.current_feature.steps_passed_percent
        self.current_feature_data['steps_failed_percent'] = self.current_feature.steps_failed_percent
        self.current_feature_data['steps_skipped_percent'] = self.current_feature.steps_skipped_percent
        self.current_feature_data['start_time'] = self.current_feature.start_time
        self.current_feature_data['end_time'] = self.current_feature.end_time
        self.current_feature_data['duration'] = self.current_feature.duration
        self.current_feature_data['operating_system'] = f"{platform.system()} {platform.release()}"
        self.current_feature_data['driver'] = self.current_feature.driver

    def add_global_data(self):
        """
            This method add global data for other purposes.
        :return:
        :rtype:
        """
        return '"global_data":'+json.dumps({
            "keyword": "global_data",
            "date": datetime.date.today().strftime("%Y/%m/%d")
        })


def update_feature_scenario_data(old_scenario, new_scenario):
    """
        This method updates the data from the old_scenario.
    :param old_scenario:
    :type old_scenario:
    :param new_scenario:
    :type new_scenario:
    :return:
    :rtype:
    """
    data = {
            "total_steps": new_scenario.total_steps,
            "steps_passed": new_scenario.steps_passed,
            "steps_failed": new_scenario.steps_failed,
            "steps_skipped": new_scenario.steps_skipped,
            "steps_passed_percent": new_scenario.steps_passed_percent,
            "steps_failed_percent": new_scenario.steps_failed_percent,
            "steps_skipped_percent": new_scenario.steps_skipped_percent,
            "start_time": new_scenario.start_time,
            "end_time": new_scenario.end_time,
            "duration": new_scenario.duration
    }
    return old_scenario.update(data)


def format_decimal(value):
    """
        This method transform a float/int to a float with 2 decimal places.
    :param value:
    :type value:
    :return:
    :rtype:
    """
    return f"{value:.2f}"
