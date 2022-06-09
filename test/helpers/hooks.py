def before_all(context):
    """Initialization method that will be executed before the test execution

    :param context: behave context
    """


def before_feature(context, feature):
    """Feature initialization

    :param context: behave context
    :param feature: running feature
    """


def before_scenario(context, scenario):
    """Scenario initialization

    :param context: behave context
    :param scenario: running scenario
    """


def after_scenario(context, scenario):
    """Clean method that will be executed after each scenario

    :param context: behave context
    :param scenario: running scenario
    """


def after_feature(context, feature):
    """Clean method that will be executed after each feature

    :param context: behave context
    :param feature: running feature
    """


def after_all(context):
    """Clean method that will be executed after all features are finished

    :param context: behave context
    """


def before_step(context, step):
    """Clean method that will be executed before step are finished

    :param step:
    :param context: behave context
    """


def after_step(context, step):
    """Clean method that will be executed after step are finished

    :param step:
    :param context: behave context
    # """
