import base64
from pathlib import Path
import datetime

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.__str__().replace("\\", "/")

STATUS_ICONS = {
    'passed': '<i class="status-success-icon"></i>',
    'failed': '<i class="status-failed-icon"></i>',
    'skipped': '<i class="status-skipped-icon"></i>'
}


def format_decimal(value):
    """
        This function format a float value to 2 decimal.
    :param value:
    :type value:
    :return:
    :rtype:
    """
    return f"{value:.2f}"


def get_duration(value):
    """
        Given the seconds its return the datetime.
    :param value:
    :type value:
    :return:
    :rtype:
    """
    return datetime.timedelta(seconds=value)


def get_datetime_from_timestamp(timestamp):
    """
        Given a timestamp return a datetime
    :param timestamp:
    :type timestamp:
    :return:
    :rtype:
    """
    return datetime.datetime.fromtimestamp(timestamp) if timestamp is not None else "-"


def get_base64_image_by_path(image_path):
    """
        Return a base64 string given an image_path.
    :param image_path:
    :type image_path:
    :return:
    :rtype:
    """
    with open(image_path, 'rb') as image:
        return base64.b64encode(image.read()).decode()
