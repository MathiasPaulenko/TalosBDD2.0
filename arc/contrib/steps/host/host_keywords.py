"""
Host Default Keywords

List of steps:
######################################################################################################################

"""
import time

from behave import use_step_matcher, step

use_step_matcher("re")


#######################################################################################################################
#                                                  Funcional Steps                                                    #
#######################################################################################################################
@step(u"open host emulator")
def open_host_emulator(context):
    """
    TODO: description
    :example
        Given open host emulator
    :
    :tag Host step:
    :param context:
    :return:
    """
    output, err, code = context.host.open_emulator()
    evidence = {
        'output': str(output),
        'err': str(err),
        'code': str(code)
    }
    context.func.add_formatter_evidence_json(evidence, "open host emulator")
    assert b'Ok' in output


@step(u"wait for value '(?P<value>.+)' in row '(?P<row>.+)', column '(?P<column>.+)' and length '(?P<length>.+)'")
def wait_for_value_emulator(context, value, row, column, length):
    """
    TODO: description
    :example
        Given wait for value 'Text' in row '23', column '2' and length '6'
    :
    :tag Host step:
    :param context:
    :param value:
    :param row:
    :param column:
    :param length:
    :return:
    """
    output, err, code = context.host.wait(row, column, length, value)
    evidence = {
        'output': str(output),
        'err': str(err),
        'code': str(code)
    }
    context.func.add_formatter_evidence_json(evidence, "wait operation")
    assert b'Ok' in output


@step(u"put the value '(?P<value>.+)' in row '(?P<row>.+)' and column '(?P<column>.+)' in emulator")
def put_value_emulator(context, value, row, column):
    """
    TODO: description
    :example
        Given put the value 'Value' in row '24' and column '2' in emulator
    :
    :tag Host step:
    :param context:
    :param value:
    :param row:
    :param column:
    :return:
    """
    output, err, code = context.host.put_value(row, column, value)
    evidence = {
        'output': str(output),
        'err': str(err),
        'code': str(code)
    }
    context.func.add_formatter_evidence_json(evidence, "put operation")
    assert b'Ok' in output


@step(u"put multiple values in emulator")
def put_multiple_value_emulator(context):
    """
    TODO: description
    :example
        Given put multiple values in emulator
          | value | row | column | interval |
          | S     | 24  | 2      | 0.5      |
          | A     | 24  | 2      | 2        |
          | B     | 24  | 2      | 1        |
    :
    :tag Host step:
    :param context:
    :return:
    """
    evidence = {}
    if context.table:
        for index, row_table in enumerate(context.table):
            value = row_table["value"]
            row = row_table["row"]
            column = row_table["column"]
            output, err, code = context.host.put_value(row, column, value)

            evidence[index] = {
                'output': str(output),
                'err': str(err),
                'code': str(code)
            }

            try:
                interval = float(row_table["interval"])
                time.sleep(interval)

            except (Exception,):
                time.sleep(1)
                pass

    context.func.add_formatter_evidence_json(evidence, "put operations")
    for key, value in evidence.items():
        assert 'Ok' in value['output']


@step(u"press '(?P<key>.+)' key in emulator")
def press_key_emulator(context, key):
    """
    TODO: description
    :example
        Given press 'enter' key in emulator

    :
    :tag Host step:
    :param context:
    :param key:
    :return:
    """
    output, err, code = context.host.send_key(key)
    evidence = {
        'output': str(output),
        'err': str(err),
        'code': str(code)
    }
    context.func.add_formatter_evidence_json(evidence, "key operation")
    assert b'Ok' in output


@step(u"press multiple keys in emulator")
def press_multiple_keys_emulator(context):
    """
    TODO: description
    :example
        Given press multiple keys in emulator
          | key   | interval |
          | enter | 0.5      |
          | tab   | 2        |
          | enter | 1        |

    :
    :tag Host step:
    :param context:
    :return:
    """
    evidence = {}
    if context.table:
        for index, row_table in enumerate(context.table):
            key = row_table["key"]
            output, err, code = context.host.send_key(key)

            evidence[index] = {
                'output': str(output),
                'err': str(err),
                'code': str(code)
            }
            try:
                interval = float(row_table["interval"])
                time.sleep(interval)

            except (Exception,):
                time.sleep(1)
                pass

    context.func.add_formatter_evidence_json(evidence, "keys operation")
    for key, value in evidence.items():
        assert 'Ok' in value['output']


@step(u"get with row '(?P<row>.+)', column '(?P<column>.+)' and length '(?P<length>.+)' in emulator")
def get_value_emulator(context, row, column, length):
    """
    TODO: description
    :example
        Given get with row '14', column '24' and length '8' in emulator

    :
    :tag Host step:
    :param context:
    :param row:
    :param column:
    :param length:
    :return:
    """
    output, err, code = context.host.get(row, column, length)
    context.host.get_value = output
    evidence = {
        'output': str(output),
        'err': str(err),
        'code': str(code)
    }
    context.func.add_formatter_evidence_json(evidence, "get operation")
    assert b'Ok' in output


@step(u"put in ftp '(?P<local_file>.+)' to '(?P<ftp_file>.+)' with emulator")
def emulator(context, local_file, ftp_file):
    """
    TODO: description
    :example
        TODO: example

    :
    :param context:
    :param local_file:
    :param ftp_file:
    :return:
    """
    output, err, code = context.host.ftp('put', local_file, ftp_file)
    evidence = {
        'output': str(output),
        'err': str(err),
        'code': str(code)
    }
    context.func.add_formatter_evidence_json(evidence, "ftp operation")
    assert b'Ok' in output


@step(u"get from ftp '(?P<ftp_file>.+)' to '(?P<local_file>.+)' with emulator")
def emulator(context, ftp_file, local_file):
    """
    TODO: description
    :example
        TODO: example

    :
    :param context:
    :param ftp_file:
    :param local_file:
    :return:
    """
    output, err, code = context.host.ftp('get', local_file, ftp_file)
    evidence = {
        'output': str(output),
        'err': str(err),
        'code': str(code)
    }
    context.func.add_formatter_evidence_json(evidence, "ftp operation")
    assert b'Ok' in output


@step(u"perform the following actions in the emulator")
def emulator(context):
    """
    TODO: description
    :example
         Given perform the following actions in the emulator
              | command | params        |
              | wait    | Teclee;23;2;6 |
              | put     | S;24;2        |
              | key     | enter         |

    :
    :tag Host step:
    :param context:
    :return:
    """
    context.host.get_value = []
    evidence = {}
    if context.table:
        for index, row_table in enumerate(context.table):
            command = row_table['command']
            params = row_table['params']

            params_list = str(params).split(';')

            output, err, code = context.host.perform_actions(command, params_list)
            evidence[index] = {
                'output': str(output),
                'err': str(err),
                'code': str(code)
            }
            print(str(output))
            context.func.add_extra_info(capture_name=index)
            if command == 'get':
                context.host.get_value.append(output)

            try:
                interval = float(row_table["interval"])
                time.sleep(interval)

            except (Exception,):
                time.sleep(1)
                pass

    context.func.add_formatter_evidence_json(evidence, "perform actions")
    for key, value in evidence.items():
        assert 'Ok' in value['output']
