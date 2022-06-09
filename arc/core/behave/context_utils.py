# -*- coding: utf-8 -*-
from settings import settings


class PyTalosContext:
    context: None

    def __init__(self, context):
        self.context = context


class RuntimeDatas:
    context = None

    def __init__(self, context):
        self.context = context


class TestData:
    context = None

    def __init__(self, context):
        self.context = context


class Settings:
    context = None

    def __init__(self, context):
        self.context = context
        self.pytalos_base_path = settings.BASE_PATH
        self.pytalos_run = settings.PYTALOS_RUN
        self.pytalos_reports = settings.PYTALOS_REPORTS
        self.pytalos_profiles = settings.PYTALOS_PROFILES
        self.pytalos_catalog = settings.PYTALOS_CATALOG
        self.pytalos_alm = settings.PYTALOS_ALM
        self.pytalos_jira = settings.PYTALOS_JIRA
        self.pytalos_behave = settings.BEHAVE

