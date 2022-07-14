from arc.reports.html.element import Element
from arc.reports.html.utils import get_duration, get_datetime_from_timestamp, STATUS_ICONS


class Scenario(Element):
    """
        This object represents a scenario.
        Parameters must be passed as kwargs.
        This object receives the following parameters:
            -name: str
            -feature_name: str
            -element_type
            -location: str
            -steps: list
            -status: str
            -total_steps: int
            -steps_passed: int
            -steps_failed: int
            -steps_passed_percent: str
            -steps_failed_percent: str
            -start_time: timestamp
            -end_time: timestamp
            -duration: float
    """
    def __init__(self, **kwargs):

        super().__init__(kwargs['element_type'], kwargs['location'], kwargs['name'])
        self.steps = kwargs['steps']
        self.tags = kwargs['tags']
        self.status = kwargs['status']
        self.total_steps = kwargs['total_steps']
        self.feature_name = kwargs['feature_name']
        self.passed_steps = kwargs['steps_passed']
        self.failed_steps = kwargs['steps_failed']
        self.skipped_steps = kwargs['steps_skipped']
        self.steps_passed_percent = kwargs['steps_passed_percent']
        self.steps_failed_percent = kwargs['steps_failed_percent']
        self.steps_skipped_percent = kwargs['steps_skipped_percent']
        self.start_time = kwargs['start_time']
        self.end_time = kwargs['end_time']
        self.duration = kwargs['duration']
        self.total_duration = get_duration(kwargs['duration'])

    def get_data(self):
        """
            This method returns a dict with scenario data.
        :return:
        :rtype:
        """
        return {
            "scenario_name": f"<a href='scenario_{self.name}.html'>{self.name}</a>",
            "tags": "<pre>"+"\n".join(self.tags)+"</pre>",
            "status": STATUS_ICONS[self.status],
            "total_steps": self.total_steps,
            "steps_passed": self.passed_steps,
            "failed_steps": self.failed_steps,
            "skipped_steps": self.skipped_steps,
            "duration": self.total_duration
        }

    def get_steps_data(self):
        """
            This method returns a list of dicts with the steps data.
        :return:
        :rtype:
        """
        return [
            {
                "name": step.get('name'),
                "status": STATUS_ICONS[step.get('result').get('status', 'skipped')] if step.get('result') else STATUS_ICONS['skipped'],
                "duration": get_duration(step.get('result').get('duration')) if step.get('result') else '-',
                "start_time": get_datetime_from_timestamp(step.get('start_time')),
                "end_time": get_datetime_from_timestamp(step.get('end_time')),
            } for step in self.steps
        ]
