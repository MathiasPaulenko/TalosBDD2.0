import json
from utils import BASE_DIR
from element import Element
from feature import Feature
from htmlGenerator import HtmlGenerator


def generate_reports():
    features = []
    with open(f'{BASE_DIR}/output/reports/talos_report.json') as json_file:
        json_data = json.load(json_file)
    for element in json_data.get("features", []):
        new_feature = Feature(
            name=element.get("name"),
            status=element.get("status"),
            tags=element.get("tags", []),
            element_type=Element.ELEMENT_FEATURE,
            location=element.get("location"),
            description=element.get("description"),
            total_scenarios=element.get("total_scenarios"),
            passed_scenarios=element.get("passed_scenarios"),
            failed_scenarios=element.get("failed_scenarios"),
            scenarios_passed_percent=element.get("scenarios_passed_percent"),
            scenarios_failed_percent=element.get("scenarios_failed_percent"),
            total_steps=element.get("total_steps"),
            steps_passed=element.get("steps_passed"),
            steps_failed=element.get("steps_failed"),
            steps_skipped=element.get("steps_skipped"),
            steps_passed_percent=element.get("steps_passed_percent"),
            steps_failed_percent=element.get("steps_failed_percent"),
            steps_skipped_percent=element.get("steps_skipped_percent"),
            start_time=element.get("start_time"),
            end_time=element.get("end_time"),
            duration=element.get("duration", 0),
            driver=element.get("driver"),
            operating_system=element.get("operating_system")
        )
        new_feature.add_elements(element.get("elements"))
        features.append(new_feature)

    HtmlGenerator(features).create_files()


generate_reports()
