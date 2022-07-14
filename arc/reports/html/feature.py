from arc.reports.html.element import Element
from arc.reports.html.scenario import Scenario
from arc.reports.html.utils import get_duration, STATUS_ICONS


class Feature(Element):
    """
        This object represents a feature.
        Parameters must be passed as kwargs.
        This object receives the following parameters:
            -name: str
            -status: str
            -tags: list
            -element_type
            -location: str
            -total_scenarios: int
            -passed_scenarios: int
            -failed_scenarios: int
            -scenarios_passed_percent: str
            -scenarios_failed_percent: str
            -total_steps: int
            -steps_passed: int
            -steps_failed: int
            -steps_passed_percent: str
            -steps_failed_percent: str
            -start_time: timestamp
            -end_time: timestamp
            -duration: float
            -description: str
    """
    def __init__(self, **kwargs):
        super().__init__(kwargs['element_type'], kwargs['location'], kwargs['name'])
        self.status = kwargs['status']
        self.tags = kwargs['tags']
        self.description = kwargs['description']

        self.total_scenarios = kwargs['total_scenarios']
        self.scenarios_passed = kwargs['passed_scenarios']
        self.scenarios_failed = kwargs['failed_scenarios']
        self.scenarios_passed_percent = kwargs['scenarios_passed_percent']
        self.scenarios_failed_percent = kwargs['scenarios_failed_percent']

        self.total_steps = kwargs['total_steps']
        self.steps_passed = kwargs['steps_passed']
        self.steps_failed = kwargs['steps_failed']
        self.steps_skipped = kwargs['steps_skipped']
        self.steps_passed_percent = kwargs['steps_passed_percent']
        self.steps_failed_percent = kwargs['steps_failed_percent']
        self.steps_skipped_percent = kwargs['steps_skipped_percent']

        self.start_time = kwargs['start_time']
        self.end_time = kwargs['end_time']
        self.duration = kwargs['duration']
        self.total_duration = get_duration(kwargs.get('duration', 0))
        self.operating_system = kwargs['operating_system']
        self.driver = kwargs['driver']
        self.scenarios = []

    def __str__(self):
        return f"Feature name: {self.name}\n" \
               f"Feature description: {self.description}"

    def add_elements(self, elements:list):
        """
            This method receives a list of scenarios
        :param elements:
        :type elements:
        :return:
        :rtype:
        """
        for element in elements:
            if element.get("type") == Element.ELEMENT_SCENARIO:
                self._add_scenario(element)

    def _add_scenario(self, element):
        """
            This method creates and add the created scenario to the scenarios list of the feature.
        :param element:
        :type element:
        :return:
        :rtype:
        """
        scenario = Scenario(
            name=element.get('name'),
            feature_name=self.name,
            element_type=Element.ELEMENT_SCENARIO,
            location=element.get("location"),
            steps=element.get("steps"),
            tags=element.get("tags"),
            status=element.get("status"),
            total_steps=element.get("total_steps"),
            steps_passed=element.get("steps_passed"),
            steps_failed=element.get("steps_failed"),
            steps_skipped=element.get("steps_skipped"),
            steps_passed_percent=element.get("steps_passed_percent"),
            steps_failed_percent=element.get("steps_failed_percent"),
            steps_skipped_percent=element.get("steps_skipped_percent"),
            start_time=element.get("start_time"),
            end_time=element.get("end_time"),
            duration=element.get("duration", 0)
        )
        self.scenarios.append(scenario)

    def get_data(self):
        """
            This method returns a dictionary with feature data.
        :return:
        :rtype:
        """
        return {
            "feature_name": f"<a href='feature_{self.name}.html'>{self.name}</a>",
            "tags": "<pre>"+"\n".join(self.tags)+"</pre>",
            "status": STATUS_ICONS[self.status],
            "os": self.operating_system,
            "driver": self.driver,
            "total_scenarios": self.total_scenarios,
            "scenarios_passed": self.scenarios_passed,
            "scenarios_failed": self.scenarios_failed,
            "total_steps": self.total_steps,
            "steps_passed": self.steps_passed,
            "steps_failed": self.steps_failed,
            "steps_skipped": self.steps_skipped,
            "duration": self.total_duration
        }
