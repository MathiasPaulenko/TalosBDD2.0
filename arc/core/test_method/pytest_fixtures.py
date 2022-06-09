# -*- coding: utf-8 -*-

import os
import pytest

from arc.core.driver.driver_manager import DriverManager


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)
    return


@pytest.yield_fixture(scope='session', autouse=True)
def session_driver_fixture(request):
    yield None
    DriverManager.close_drivers(scope='session',
                                test_name=request.node.name,
                                test_passed=request.session.testsfailed == 0)


@pytest.yield_fixture(scope='module', autouse=True)
def module_driver_fixture(request):
    previous_fails = request.session.testsfailed
    yield None
    DriverManager.close_drivers(scope='module',
                                test_name=os.path.splitext(os.path.basename(request.node.name))[0],
                                test_passed=request.session.testsfailed == previous_fails)


@pytest.yield_fixture(scope='function', autouse=True)
def driver_wrapper(request):
    default_driver_wrapper = DriverManager.connect_default_driver_wrapper()
    yield default_driver_wrapper
    DriverManager.close_drivers(scope='function',
                                test_name=request.node.name,
                                test_passed=not request.node.rep_call.failed)
