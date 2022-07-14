try:
    import paramiko
except ImportError:
    pass
import base64
import socket


class WrapperSFTP:
    """ A wrapper for SFTP connections """
    hostname = None
    port = None
    username = None
    password = None
    sftp_connection = None

    def __init__(self, hostname, port, username, password):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        if 'paramiko' not in globals():
            raise Exception('Paramiko is not installed. You must install it using the command "pip install paramiko==2.11.0" to use this functionality')

    def open_connection(self):
        """
        Create a new connection with a SFTP server, is not possible to create more than one session
        at the same time, if you try to open a second session the first one will be closed.
        """
        password_decoded = base64.b64decode(self.password)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.hostname, self.port))
        transport = paramiko.Transport(sock)
        transport.start_client()
        transport.auth_password(self.username, password_decoded, fallback=False)
        if self.sftp_connection:
            if not self.sftp_connection.sock.closed:
                self.sftp_connection.close()
        self.sftp_connection = paramiko.SFTPClient.from_transport(transport)

    def close_connection(self):
        """
        Close the session with the SFTP server
        """
        self.sftp_connection.close()

    def set_sftp_parameters(self, hostname, port, username, password):
        """
        Set the parameters to connect to the SFTP server
        Input:
            hostname: name of the host
            port: port to connect to the host
            username: required to authenticate with SFTP
            password: required to authenticate with SFTP
        """
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password

    def get_sftp_parameters(self):
        """
        Return the credentials of the SFTP server connected
        Output:
            Return credential of SFTP server
        """
        dict_sftp_parameters = {
            'hostname': self.hostname,
            'port': self.port,
            'username': self.username,
            'password': self.password,
        }
        return dict_sftp_parameters

    def change_dir(self, path):
        """
        Change the current path in the server
        Input:
            path: end path
        """
        self.sftp_connection.chdir(path)

    def list_dir(self):
        """
        List the contain of the current directory
        Output:
            return a list with the contain of the directory
        """
        return self.sftp_connection.listdir()

    def get_current_dir(self):
        """
        Get the current path
        Output:
            Return the current path from SFTP
        """
        return self.sftp_connection.getcwd()

    def parent_directory(self):
        """Up to parent directory"""
        current_path = self.sftp_connection.getcwd()
        index = current_path.rfind('/')
        parent_path = current_path[:index]
        self.sftp_connection.chdir(parent_path)

    def get_file(self, remote_path, local_path):
        """
        Copy a remote file remote_path from the SFTP server to the local host as local_path
        Input:
            remote_path: the remote file to copy
            local_path: the destination path on the local host
        """
        self.sftp_connection.get(remote_path, local_path)

    def put_file(self, local_path, remote_path):
        """
        Copy a local file local_path to the SFTP server as remote_path.
        Input:
            local_path: the local file to copy
            remote_path: the destination path on the SFTP
        Output:

        """
        return self.sftp_connection.put(local_path, remote_path)

    def delete_file(self, file_path):
        """
        Remove the file at the given path.
        Input:
            file_path: path (absolute or relative) of the file to remove
        """
        self.sftp_connection.remove(file_path)

    def delete_folder(self, directory_path):
        """
        Remove the folder at the given path.
        Input:
            directory_path: path (absolute or relative) of the folder to remove
        """
        self.sftp_connection.rmdir(directory_path)

    def rename(self, old_name, new_name):
        """
        Rename a file or folder from oldpath to newpath.
        Input:
            old_name: existing name of the file or folder
            new_name: new name for the file or folder, must not exist already
        """
        self.sftp_connection.rename(old_name, new_name)

    def create_dir(self, path):
        """
        Create a folder named path
        Input:
            path: name of the directory to create
        """
        self.sftp_connection.mkdir(path)

    def get_session(self):
        """
        Return SFTP session
        Output:
            SFTP session
        """
        return self.sftp_connection
