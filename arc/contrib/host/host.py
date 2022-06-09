import subprocess

from arc.settings import settings


class Host:

    def __init__(self, ws_path, cscript):
        self.cscript = cscript
        self.ws_path = ws_path
        self.vs_middleware = settings.VS_MIDDLEWARE
        self.execute = subprocess.Popen

    def open_emulator(self):
        output, err, code = self.execute_command('open', [self.ws_path, ])
        assert code == 0
        return output, err, code

    def close_emulator(self):
        output, err, code = self.execute_command('close')
        assert code == 0
        return output, err, code

    def put_value(self, row, column, value):
        output, err, code = self.execute_command('put', [row, column, value])
        return output, err, code

    def wait(self, row, column, length, value):
        output, err, code = self.execute_command('wait', [row, column, length, value])
        return output, err, code

    def send_key(self, key):
        output, err, code = self.execute_command('key', [key, ])
        return output, err, code

    def get(self, row, column, length):
        output, err, code = self.execute_command('get', [row, column, length])
        return output, err, code

    def ftp(self, operation_type, pc_file_name, host_file_name):
        output, err, code = self.execute_command('ftp', [operation_type, pc_file_name, host_file_name])
        return output, err, code

    def execute_command(self, command, vs_args=None):
        if vs_args is None:
            vs_args = []

        p = self.execute(
            [self.cscript, self.vs_middleware, command] + vs_args,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        output, err = p.communicate()
        code = p.returncode

        return output, err, code

    def perform_actions(self, command, params):
        if command == 'put':
            if len(params) == 3:
                return self.put_value(params[1], params[2], params[0])
            else:
                raise Exception("3 parameters expected for PUT command\n"
                                "Mandatory parameters: value, row and column\n"
                                "For example: aValue;24;2")
        elif command == 'wait':
            if len(params) == 4:
                return self.wait(params[1], params[2], params[3], params[0])

            else:
                raise Exception("4 parameters expected for WAIT command\n"
                                "Mandatory parameters: value, row, column and length \n"
                                "For example: aValue;23;3;6")
        elif command == 'key':
            if len(params) == 1:
                return self.send_key(params[0])

            else:
                raise Exception("1 parameters expected for KEY command\n"
                                "Mandatory parameters: key \n"
                                "For example: enter")
        elif command == 'get':
            if len(params) == 3:
                return self.get(params[0], params[1], params[3])
            else:
                raise Exception("3 parameters expected for GET command\n"
                                "Mandatory parameters: row, column and length \n"
                                "For example: 23;32;6")

        else:
            raise Exception("Command not allowed\n"
                            "Accepted commands:: put, wait, key and get")
