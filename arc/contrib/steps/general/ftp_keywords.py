"""
FTP Default Keywords
Default steps for use in Gherkin features.
In each step there is the documentation of what it is for and how to use it, as well as an example.
In some steps, not only is the desired operation performed, but it also adds extra information to the Word evidence.

List of steps:
######################################################################################################################

## Connect Steps:
connect to host {host} with username {username} and password {password}
connect to FTP host with data table
connect to host {host} with username {username} and password {password} with options
close FTP connection

## FPT Get Steps
download file {remote_file_path} from FTP server in local file {local_file_path}
download file from FTP server in local file
save the content of the file {remote_file_path} in the context variable
add to the profile file {file_name} and key {key} the FPT file {remote_path} content
saves in the context variable a list of files in the remote directory {remote_path}
saves in the context variable a complete list of files in the remote directory {remote_path}
add to the profile file {file_name} and key {key} the FPT path {remote_path} files
add to the profile file {name} and key {key} the FPT path {remote_path} complete files

## FTP Put Steps
upload the file {local_file_path} to the FTP server in the path {remote_file_path}
upload a file to the FTP server
upload multiple files to FTP server
put the text {text} in the file {remote_file_path} of the FTP server
insert the text {text} in the file {remote_file_path} of the FTP server
generate remote directory tree {tree} from local path {local_path}

## FTP Actions Steps
go to directory {remote_path}
create directory {dir_name}
delete file {remote_file_path}
saves in the context variable the current directory path
(rename|move) the remote file {remote_file_path} to {remote_file_path_to}
saves in the context variable the current FTP server session

SFTP Default Keywords
Default steps for use in Gherkin features.
In each step there is the documentation of what it is for and how to use it, as well as an example.
In some steps, not only is the desired operation performed, but it also adds extra information to the Word evidence.

List of steps:
######################################################################################################################

## Connect Steps:
connect to SFTP server with host {host} username {username} port{port} and password {password}
connect to SFTP host with data table
close SFTP connection

## SFPT Get Steps
download file {remote_file_path} from SFTP server in local file {local_file_path}
download file from FTP server in local file
save the content of the file {remote_file_path} in the context variable
saves in the context variable a list of files in the remote directory {remote_path}

## SFTP Put Steps
upload the file {local_file_path} to the SFTP server in the path {remote_file_path}
upload a file to the SFTP server
upload multiple files to SFTP server
generate remote directory tree {tree} from local path {local_path}

## SFTP Actions Steps
go to directory in SFTP server {remote_path}
create directory in SFTP server {dir_name}
delete file in SFTP server {remote_file_path}
saves in the context variable the current directory path from SFTP server
(rename|move) the remote file {remote_file_path} to {remote_file_path_to} in SFTP server
saves in the context variable the current SFTP server session
"""
from distutils.util import strtobool

from behave import use_step_matcher, step
from arc.contrib.tools import files, sftp

use_step_matcher("re")


#######################################################################################################################
#                                                  Connect Steps                                                      #
#######################################################################################################################
@step(u"connect to host '(?P<host>.+)' with username '(?P<username>.+)' and password '(?P<password>.+)'")
def ftp_connect(context, host, username, password):
    """
    This step connects to the FTP server with the username and password indicated in the parameterization
    :example
        Given connect to FTP host 'ftp:host' with username 'username' and password 'password'
    :
    :tag FTP Connect:
    :param context:
    :param host:
    :param username:
    :param password:
    :return test_ftp_connect_data:
    """

    context.ftp.connect(host, username, password)
    dict_evidence = {
        'host': host,
        'username': username,
        'password': password
    }
    context.func.add_formatter_evidence_json(dict_evidence, "FTP Connect")
    context.test_ftp_connect_data = dict_evidence


@step(u"connect to FTP host with data table")
def ftp_connect_data_table(context):
    """
    This step connects to the FTP server with the username and password indicated in the data table
    You can also parameterize the values of "secure" and "passive" optionally
    :example
            Given connect to FTP host with data table
              | param    | value     |
              | host     | ftp.host  |
              | username | username  |
              | password | password  |
              | passive  | False     |
              | secure   | False     |
    :
    :tag FTP Connect:
    :param context:
    :return context.test_ftp_connect_data:
    """
    dict_conn = {}
    if context.table:
        for row in context.table:
            if context.func.is_contains_profile_re_var(row["value"]):
                value = context.func.get_unique_profile_re_var(row["value"], context.master_file_name_config)
            else:
                value = row["value"]

            dict_conn[row["param"]] = value
    try:
        if 'secure' in dict_conn.keys():
            dict_conn['secure'] = bool(strtobool(dict_conn['secure']))
        else:
            dict_conn['secure'] = False
        if 'passive' in dict_conn.keys():
            dict_conn['passive'] = bool(strtobool(dict_conn['passive']))
        else:
            dict_conn['passive'] = True
    except Exception as ex:
        print(ex)
        raise Exception("The parameters 'secure', 'passive' and 'ftp_conn' must be Boolean")

    context.ftp.connect(
        host=dict_conn['host'],
        user=dict_conn['username'],
        password=dict_conn['password'],
        secure=dict_conn['secure'],
        passive=dict_conn['passive']
    )

    context.func.add_formatter_evidence_json(dict_conn, "FTP Connect")
    context.test_ftp_connect_data = dict_conn


@step(u"connect to host '(?P<host>.+)' with username '(?P<username>.+)' and password '(?P<password>.+)' with options")
def ftp_connect_with_options(context, host, username, password):
    """
    This step connects to the FTP server with the username and password indicated in the parameterization
    You can also enter the values of the parameters "secure" and "passive"
    in a data table of boolean values.
    :example
        Given connect to host 'ftp.host' with username 'username' and password 'password' with options
              | param   | value |
              | passive | False |
    :
    :tag FTP Connect:
    :param context:
    :param host:
    :param username:
    :param password:
    :return context.test_ftp_connect_data:
    """
    dict_conn = {}
    if context.table:
        for row in context.table:
            if context.func.is_contains_profile_re_var(row["value"]):
                value = context.func.get_unique_profile_re_var(row["value"], context.master_file_name_config)
            else:
                value = row["value"]

            dict_conn[row["param"]] = value
    try:
        if 'secure' in dict_conn.keys():
            dict_conn['secure'] = bool(strtobool(dict_conn['secure']))
        else:
            dict_conn['secure'] = False
        if 'passive' in dict_conn.keys():
            dict_conn['passive'] = bool(strtobool(dict_conn['passive']))
        else:
            dict_conn['passive'] = True
    except Exception as ex:
        print(ex)
        raise Exception("The parameters 'secure', 'passive' and 'ftp_conn' must be Boolean")

    context.ftp.connect(host, username, password, secure=dict_conn['secure'], passive=dict_conn['passive'])
    context.func.add_formatter_evidence_json(dict_conn, "FTP Connect")
    context.test_ftp_connect_data = dict_conn


@step(u"close FTP connection")
def ftp_disconnect(context):
    """
    Close the FTP connection
    :example
        Then close FTP connection
    :
    :tag FTP Connect:
    :param context:
    :return:
    """
    context.ftp.close_connection()


#######################################################################################################################
#                                                  FTP Get Steps                                                      #
#######################################################################################################################
@step(u"download file '(?P<remote_file_path>.+)' from FTP server in local file '(?P<local_file_path>.+)'")
def ftp_download_parameter(context, remote_file_path, local_file_path):
    """
    Download the file passed by parameter and save it in the local path and name also passed by parameter
    :example
        Given download file '/1/2021/03/07/photo.jpg' from FTP server in local file 'download/aphoto_copy.jpg'

        Given download file '/1/2021/03/07/photo.jpg' from FTP server in local file 'download/aphoto.jpg'
    :
    :tag FTP Get Action:
    :param context:
    :param remote_file_path:
    :param local_file_path:
    :return context.test_ftp_get:
    """
    dict_evidence = {
        'local file path': local_file_path,
        'remote file path': remote_file_path
    }
    context.ftp.get_file_and_save(remote_file_path, local_file_path)
    context.func.add_formatter_evidence_json(dict_evidence, "FTP Download file")
    verification = files.is_file_exist(local_file_path)
    context.func.generate_table_evidence("Check if the file was downloaded correctly", value_expected=str(True),
                                         result_flag=str(verification))

    context.test_ftp_get = dict_evidence


@step(u"download file from FTP server in local file")
def ftp_download_data_table(context):
    """
    Download the file using the path and remote file name and save it in a directory passed by parameter.
    Both the remote and local file path parameters must be passed through a data table.
    said data table will contain the parameter "remote_path" and the parameter "local_path"
    :example
            Given download file from FTP server in local file
              | param       | value                   |
              | remote_path | /1/2021/03/07/image.jpg |
              | local_path  | download/image.jpg      |
    :
    :tag FTP Get Action:
    :param context:
    :return context.test_ftp_get:
    """
    dict_conn = {}
    if context.table:
        for row in context.table:
            if context.func.is_contains_profile_re_var(row["value"]):
                value = context.func.get_unique_profile_re_var(row["value"], context.master_file_name_config)
            else:
                value = row["value"]

            dict_conn[row["param"]] = value

    dict_evidence = {
        'local file path': dict_conn['local_path'],
        'remote file path': dict_conn['remote_path']
    }
    context.func.add_formatter_evidence_json(dict_evidence, "FTP Download file")
    context.ftp.get_file_and_save(dict_conn['remote_path'], dict_conn['local_path'])
    context.test_ftp_get = dict_evidence

    verification = files.is_file_exist(dict_conn['local_path'])
    context.func.generate_table_evidence("Check if the file was downloaded correctly", value_expected=str(True),
                                         result_flag=str(verification))


@step(u"save the content of the file '(?P<remote_file_path>.+)' in the context variable")
def ftp_save_file_content_context(context, remote_file_path):
    """
    Saves the content of a file through its remote path in the context variable: context.test_ftp_content
    The content of the file is returned in binary data type
    :example
        Given save the content of the file '/1/2021/text.txt' in the context variable
    :
    :tag FTP Get Action:
    :param context:
    :param remote_file_path:
    :return context.test_ftp_content:
    """
    context.test_ftp_content = context.ftp.get_content_file(remote_file_path)
    dict_file = {'remote file path': remote_file_path}
    dict_content = {'content': str(context.test_ftp_content)}
    context.func.add_formatter_evidence_json(dict_file, "FTP Get File Path")
    context.func.add_formatter_evidence_json(dict_content, "FTP Get File Content")
    dict_evidence = {**dict_file, **dict_content}
    context.test_ftp_content_dict = dict_evidence

    verification = context.test_ftp_content is not None
    context.func.generate_table_evidence("Check if the content was saved correctly", value_expected=str(True),
                                         result_flag=str(verification))


@step(u"add to the profile file '(?P<file_name>.+)' and key '(?P<key>.+)' the FPT file '(?P<remote_path>.+)' content")
def ftp_save_file_content_profile(context, file_name, key, remote_path):
    """
    Add the content of the remote file in a profile file with the name of the
    file and its corresponding key passed by parameter
    The content of the file is returned in binary data type
    :example
            Given add to the profile file 'master' and 'content' the FPT file '/1/2021/text.txt' content
    :
    :tag FTP Get Action:
    :param context:
    :param key:
    :param remote_path:
    :param file_name:
    :return context.test_ftp_content:
    """
    test_ftp_content = context.ftp.get_content_file(remote_path)
    dict_file = {'remote file path': remote_path}
    dict_content = {'content': str(test_ftp_content)}
    context.func.add_formatter_evidence_json(dict_file, "FTP Get File Path")
    context.func.add_formatter_evidence_json(dict_content, "FTP Get File Content")
    dict_evidence = {**dict_file, **dict_content}
    files.set_profile_data_value(file_name, key, dict_evidence, change_all_profiles=True)
    context.test_ftp_content_dict = dict_evidence


@step(u"saves in the context variable a list of files in the remote directory '(?P<remote_path>.+)'")
def ftp_save_file_directory_list(context, remote_path):
    """
    saves a list of files of the remote directory in the context variable: context.test_ftp_list_files
     :example
        Given saves in the context variable a list of files in the remote directory '/remote/path'
    :
    :tag FTP Get Action:
    :param context:
    :param remote_path:
    :return:
    """
    context.test_ftp_list_files = context.ftp.get_file_list_in_directory(remote_path)
    dict_file = {
        'remote file path': remote_path,
        'files': context.test_ftp_list_files
    }
    context.func.add_formatter_evidence_json(dict_file, "FTP File Directory")

    verification = context.test_ftp_list_files is not None
    context.func.generate_table_evidence("Check if the list file was saved correctly", value_expected=str(True),
                                         result_flag=str(verification))


@step(u"saves in the context variable a complete list of files in the remote directory '(?P<remote_path>.+)'")
def ftp_save_complete_file_directory_list(context, remote_path):
    """
    saves a complete list of files of the remote directory in the context variable: context.test_ftp_list_files
     :example
        Given saves in the context variable a complete list of files in the remote directory '/remote/path'
    :
    :tag FTP Get Action:
    :param context:
    :param remote_path:
    :return:
    """
    context.test_ftp_list_files = context.ftp.get_complete_file_list_in_directory(remote_path)
    dict_file = {
        'remote file path': remote_path,
        'files': context.test_ftp_list_files
    }
    context.func.add_formatter_evidence_json(dict_file, "FTP File Directory")
    verification = context.test_ftp_list_files is not None
    context.func.generate_table_evidence("Check if the complete list file was saved correctly",
                                         value_expected=str(True), result_flag=str(verification))


@step(u"add to the profile file '(?P<file_name>.+)' and key '(?P<key>.+)' the FPT path '(?P<remote_path>.+)' files")
def ftp_add_profile_file_directory_list(context, file_name, key, remote_path):
    """
    save in the profile file and key passed by parameter the list of files
    that are in the remote path also passed by parameter
    :example
           Given add to the profile file 'master' and key 'file_dir' the FPT path 'test/generate/test2/' files
    :
    :tag FTP Get Action:
    :param context:
    :param file_name:
    :param key:
    :param remote_path:
    :return:
    """
    test_ftp_list_files = context.ftp.get_file_list_in_directory(remote_path)
    dict_file = {
        'remote file path': remote_path,
        'files': test_ftp_list_files
    }
    files.set_profile_data_value(file_name, key, dict_file, change_all_profiles=True)
    context.func.add_formatter_evidence_json(dict_file, "FTP File Directory")
    context.test_ftp_list_files = dict_file


@step(u"add to the profile file '(?P<name>.+)' and key '(?P<key>.+)' the FPT path '(?P<remote_path>.+)' complete files")
def ftp_add_profile_complete_file_directory_list(context, name, key, remote_path):
    """
    save in the profile file and key passed by parameter the complete list of files
    that are in the remote path also passed by parameter
    :example
        Given add to the profile file 'master' and key 'file_dir2' the FPT path '/1/2021' complete files

    :
    :tag FTP Get Action:
    :param context:
    :param name:
    :param key:
    :param remote_path:
    :return:
    """
    test_ftp_list_files = context.ftp.get_complete_file_list_in_directory(remote_path)
    dict_file = {
        'remote file path': remote_path,
        'files': test_ftp_list_files
    }
    files.set_profile_data_value(name, key, dict_file, change_all_profiles=True)
    context.func.add_formatter_evidence_json(dict_file, "FTP File Directory")
    context.test_ftp_list_files = dict_file


#######################################################################################################################
#                                                  FTP Put Steps                                                      #
#######################################################################################################################
@step(u"upload the file '(?P<local_file_path>.+)' to the FTP server in the path '(?P<remote_file_path>.+)'")
def ftp_put_file(context, local_file_path, remote_file_path):
    """
    upload a file using the path and name of the file to the FTP server, indicating
    the path and name of the remote file by parameterization.
    :example
        Given upload the file 'download/test.txt' to the FTP server in the path '/1/2021/03/test.txt'
    :
    :tag FTP Put Action:
    :param context:
    :param local_file_path:
    :param remote_file_path:
    :return context.test_ftp_put:
    """
    size = context.ftp.put_new_remote_file(local_file_path, remote_file_path)
    dict_evidence = {
        'local file path': local_file_path,
        'remote file path': remote_file_path,
        'size': str(size)
    }
    context.func.add_formatter_evidence_json(dict_evidence, "FTP Upload file")
    context.test_ftp_put = dict_evidence
    verification = size is not None
    context.func.generate_table_evidence("Check if the file was uploaded correctly",
                                         value_expected=str(True), result_flag=str(verification))


@step(u"upload a file to the FTP server")
def ftp_put_file_data_table(context):
    """
    Upload a file to the FTP server using a data table
    The data table must have the header "param" and "value"
    the parameters for the column of "param" must be "local_path" and "remote_path" obligatorily
    For the column "value" must be paths with file name
    :example
        Given upload a file to the FTP server
          | param       | value                |
          | local_path  | download/test.txt    |
          | remote_path | /1/2021/03/test2.txt |
    :
    :tag FTP Put Action:
    :param context:
    :return:
    """
    dict_conn = {}
    if context.table:
        for row in context.table:
            if context.func.is_contains_profile_re_var(row["value"]):
                value = context.func.get_unique_profile_re_var(row["value"], context.master_file_name_config)
            else:
                value = row["value"]

            dict_conn[row["param"]] = value

    size = context.ftp.put_new_remote_file(dict_conn['local_path'], dict_conn['remote_path'])
    dict_evidence = {
        'local file path': dict_conn['local_path'],
        'remote file path': dict_conn['remote_path'],
        'size': str(size)
    }
    context.func.add_formatter_evidence_json(dict_evidence, "FTP Upload file")
    context.test_ftp_put = dict_evidence
    verification = size is not None
    context.func.generate_table_evidence("Check if the file was uploaded correctly",
                                         value_expected=str(True), result_flag=str(verification))


@step(u"upload multiple files to FTP server")
def ftp_multiple_files(context):
    """
    Upload multiple files to the FTP server using a data table
    The data table must have the header "local" and "remote"
    the parameters for the column of "remote" must be the remote file path
    the parameters for the column of "local" must be the local file path
    :example
        Given upload multiple files to FTP server
          | local                | remote                |
          | download/test.txt    | download/test11.txt   |
          | download/weather.jpg | download/weather1.jpg |
    :
    :tag FTP Put Action:
    :param context:
    :return context.test_ftp_put:
    """
    dict_files = {}
    file_count = 1
    if context.table:
        for row in context.table:
            dict_conn = {}
            if context.func.is_contains_profile_re_var(row["remote"]):
                value_remote = context.func.get_unique_profile_re_var(row["remote"], context.master_file_name_config)
            else:
                value_remote = row["remote"]
            if context.func.is_contains_profile_re_var(row["local"]):
                value_local = context.func.get_unique_profile_re_var(row["local"], context.master_file_name_config)
            else:
                value_local = row["local"]

            dict_conn['remote'] = value_remote
            dict_conn['local'] = value_local
            dict_files[f'file {file_count}'] = dict_conn
            file_count += 1

    verification = True
    error_msg = None
    for test_files in dict_files:
        try:
            paths = dict_files[test_files]
            context.ftp.put_new_remote_file(paths['local'], paths['remote'])
        except Exception as ex:
            verification = False
            error_msg = ex

    context.func.add_formatter_evidence_json(dict_files, "FTP Upload Multiple Files")
    context.test_ftp_put = dict_files
    context.func.generate_table_evidence("Check if the files were uploaded correctly",
                                         value_expected=str(True), result_flag=str(verification),
                                         error_message=error_msg)
    if verification is not True:
        raise Exception(error_msg)


@step(u"put the text '(?P<text>.+)' in the file '(?P<remote_file_path>.+)' of the FTP server")
def ftp_put_text(context, text, remote_file_path):
    """
    Modifies the text of a file on the FTP server passing it the path of the remote file and the text to be entered
    This step replaces the original text with the new text
    :example
        Given put the text 'this is a text' in the file 'download/test.txt' of the FTP server

    :
    :tag FTP Put Action:
    :param context:
    :param text:
    :param remote_file_path:
    :return context.test_ftp_put:
    """
    size = context.ftp.put_using_string_data(remote_file_path, text)
    dict_evidence = {
        'text': text,
        'remote file path': remote_file_path,
        'size': str(size)
    }
    context.func.add_formatter_evidence_json(dict_evidence, "FTP Upload Text in File")
    context.test_ftp_put = dict_evidence
    verification = size is not None
    context.func.generate_table_evidence("Check if the text was modified correctly",
                                         value_expected=str(True), result_flag=str(verification))


@step(u"insert the text '(?P<text>.+)' in the file '(?P<remote_file_path>.+)' of the FTP server")
def ftp_insert_text(context, text, remote_file_path):
    """
    Insert the text of a file on the FTP server passing it the path of the remote file and the text to be entered
    This step does not replace the original text with the new text
    :example
        Given insert the text 'this is a text' in the file 'download/test.txt' of the FTP server

    :
    :tag FTP Put Action:
    :param context:
    :param text:
    :param remote_file_path:
    :return context.test_ftp_insert:
    """

    content = str(context.ftp.get_content_file(remote_file_path))
    content += '\n' + text
    size = context.ftp.put_using_string_data(remote_file_path, content)
    dict_evidence = {
        'text': text,
        'remote file path': remote_file_path,
        'size': str(size)
    }
    context.func.add_formatter_evidence_json(dict_evidence, "FTP Upload Text in File")
    context.test_ftp_insert = dict_evidence
    verification = size is not None
    context.func.generate_table_evidence("Check if the text was inserted correctly",
                                         value_expected=str(True), result_flag=str(verification))


@step(u"generate remote directory tree '(?P<tree>.+)' from local path '(?P<local_path>.+)'")
def ftp_generate_directory_tree(context, tree, local_path):
    """
    Put a tree on a remote directory (similar to shutil.copytree)
    where "tree" is the destination of the FTP server and "local_path" is the eating of the tree to be copied
    :example
        Given generate remote directory tree 'test/generate/test2/' from local path 'download/'
    :
    :tag FTP Put Action:
    :param context:
    :param tree:
    :param local_path:
    :return:
    """
    dict_evidence = {
        'remote tree path': tree,
        'local tree path': local_path
    }
    context.ftp.put_tree_on_remote_directory(local_path, tree)
    context.func.add_formatter_evidence_json(dict_evidence, "FTP Generate Tree")
    dst = context.test_ftp_tree = dict_evidence
    verification = dst is not None
    context.func.generate_table_evidence("Check if the directory tree was created correctly",
                                         value_expected=str(True), result_flag=str(verification))


#######################################################################################################################
#                                              FTP Actions Steps                                                      #
#######################################################################################################################
@step(u"go to directory '(?P<remote_path>.+)'")
def ftp_go_to_directory(context, remote_path):
    """
    Change the current directory of the session to the FTP server to the new directory passed by parameter
    It has the same functionality as the cd command
    :example
            Given go to directory '/1/2021'
            And go to directory '/2/2021'
    :
    :tag FTP General Actions
    :param context:
    :param remote_path:
    :return:
    """
    current_path = context.ftp.current_dir()
    new_path = context.ftp.change_directory(remote_path)
    dict_evidence = {
        'current path': current_path,
        'remote_path': new_path
    }
    context.func.add_formatter_evidence_json(dict_evidence, "FTP Go to Directory")
    context.test_ftp_actions = dict_evidence
    verification = new_path == remote_path
    context.func.generate_table_evidence("Check if directory was changed correctly",
                                         value_expected=str(remote_path), result_flag=str(verification))


@step(u"create directory '(?P<dir_name>.+)'")
def ftp_create_dir(context, dir_name):
    """
    Create a directory in the remote path passed by parameter the new directory name
    :example
        Given create directory 'test'
    :
    :tag FTP General Actions
    :param context:
    :param dir_name:
    :return context.test_ftp_actions:
    """
    new_dir = context.ftp.create_directory(dir_name)
    dict_evidence = {
        'new_directory': dir_name
    }
    context.func.add_formatter_evidence_json(dict_evidence, "FTP Create Directory")
    context.test_ftp_actions = dict_evidence
    verification = new_dir is not None
    context.func.generate_table_evidence("Verify that the directory was created correctly",
                                         value_expected=str(verification), result_flag=str(verification))


@step(u"create multiple directory in '(?P<remote_path>.+)'")
def ftp_create_multi_dir(context, remote_path):
    """
    Create multiple directory in the remote path passed by parameter
    :example
       Given create multiple directory in 'test/test1/test2'
    :
    :tag FTP General Actions
    :param context:
    :param remote_path:
    :return context.test_ftp_actions:
    """

    list_dir = remote_path.split('/')
    verification = True
    error_msg = None
    try:
        for directory in list_dir:
            context.ftp.create_directory(directory)
            context.ftp.change_directory(directory)
    except Exception as ex:
        verification = False
        error_msg = ex

    dict_evidence = {
        'new_directory': remote_path
    }
    context.func.add_formatter_evidence_json(dict_evidence, "FTP Create Multiple Directory")
    context.test_ftp_actions = dict_evidence

    context.func.generate_table_evidence("Check if the files were uploaded correctly",
                                         value_expected=str(True), result_flag=str(verification),
                                         error_message=error_msg)
    if verification is not True:
        raise Exception(error_msg)


@step(u"delete file '(?P<remote_file_path>.+)'")
def ftp_delete_file(context, remote_file_path):
    """
    Delete file in the remote path passed by parameter
    :example
       Given delete file '/1/2021/text.txt'
    :
    :tag FTP General Actions
    :param context:
    :param remote_file_path:
    :return context.test_ftp_actions:
    """
    was_deleted = context.ftp.delete_file(remote_file_path)
    dict_evidence = {
        'delete_file': remote_file_path
    }
    context.func.add_formatter_evidence_json(dict_evidence, "FTP Delete File")
    context.test_ftp_actions = dict_evidence
    verification = was_deleted is not True
    context.func.generate_table_evidence("Check if the files were deleted correctly",
                                         value_expected=str(True), result_flag=str(verification))


@step(u"saves in the context variable the current directory path")
def ftp_save_current_dir_context(context):
    """
    Saves in the context variable "context.test_ftp_current_dir" the current directory path of the FTP server
    :example
        Given saves in the context variable the current directory path
    :
    :tag FTP General Actions
    :param context:
    :return context.test_ftp_current_dir:
    """
    context.test_ftp_current_dir = context.ftp.current_dir()
    dict_file = {
        'current_directory_path': context.test_ftp_current_dir
    }
    context.func.add_formatter_evidence_json(dict_file, "FTP Save Current Directory Path")
    verification = context.test_ftp_current_dir is not None
    context.func.generate_table_evidence("Verify that the current directory was saved correctly",
                                         value_expected=str(True), result_flag=str(verification))


@step(u"(rename|move) the remote file '(?P<remote_file_path>.+)' to '(?P<remote_file_path_to>.+)'")
def ftp_rename_move_file(context, selection, remote_file_path, remote_file_path_to):
    """
    Move or rename a file using its source path and destination path
    :example
        Given rename the remote file '/1/2021/image.jpg' to '/1/2021/rename_image.jpg'

        Given move the remote file '/1/2021/image.jpg' to '/other/path/image.jpg'

        Given move the remote file '/1/2021/image.jpg' to '/other/path/rename_image.jpg'
    :
    :tag FTP General Actions
    :param context:
    :param selection:
    :param remote_file_path:
    :param remote_file_path_to:
    :return context.test_ftp_rename_move:
    """
    dst = context.ftp.rename_remote_file(remote_file_path, remote_file_path_to)
    dict_file = {
        'remote_file_name_to': remote_file_path_to,
        'remote_file_name_from': remote_file_path
    }
    context.func.add_formatter_evidence_json(dict_file, f"FTP {selection} File")
    context.test_ftp_rename_move = dict_file
    verification = dst is not None
    context.func.generate_table_evidence("Verify that the file was moved and renamed correctly",
                                         value_expected=str(True), result_flag=str(verification))


@step(u"saves in the context variable the current FTP server session")
def ftp_save_current_session_context(context):
    """
    Saves in the context variable "context.test_ftp_current_session" the current FTP server session
    :example
        Given saves in the context variable the current FTP server session
    :
    :tag FTP General Actions
    :param context:
    :return context.test_ftp_current_session:
    """
    context.test_ftp_current_session = context.ftp.get_ftp_session()
    dict_file = {
        'current_session': str(context.test_ftp_current_session)
    }
    context.func.add_formatter_evidence_json(dict_file, "FTP Save Current Session")
    verification = context.test_ftp_current_session is not None
    context.func.generate_table_evidence("Verify that the current session was saved correctly",
                                         value_expected=str(True), result_flag=str(verification))


"""
SFTP STEPS
"""

#######################################################################################################################
#                                                  Connect Steps                                                      #
#######################################################################################################################


@step(u"connect to SFTP server with host '(?P<host>.+)' username '(?P<username>.+)' port '(?P<port>.+)' and password "
      u"'(?P<password>.+)'")
def sftp_open_connect(context, host, username, port, password):
    """
    This step connects to the SFTP server with the username and password indicated in the parameterization
    :example
        Given connect to SFTP host 'sftp:host' port 'sftp:port' with username 'username' and password 'password'
    :
    :tag SFTP Connect:
    :param context:
    :param host:
    :param port:
    :param username:
    :param password:
    :return test_ftp_connect_data:
    """
    context.sftp_session = sftp.WrapperSFTP(hostname=host, port=int(port), username=username, password=password)
    context.sftp_session.open_connection()
    dict_evidence = {
        'host': host,
        'port': port,
        'username': username,
        'password': password
    }
    context.func.add_formatter_evidence_json(dict_evidence, "SFTP Connect")
    context.test_ftp_connect_data = dict_evidence


@step(u"connect to SFTP host with data table")
def sftp_connect_data_table(context):
    """
    This step connects to the SFTP server with the username and password indicated in the data table
    :example
            Given connect to SFTP host with data table
              | param    | value     |
              | host     | sftp.host  |
              | port     | sftp.port  |
              | username | username  |
              | password | password  |
    :
    :tag SFTP Connect:
    :param context:
    :return context.test_ftp_connect_data:
    """
    dict_conn = {}
    if context.table:
        for row in context.table:
            if context.func.is_contains_profile_re_var(row["value"]):
                value = context.func.get_unique_profile_re_var(row["value"], context.master_file_name_config)
            else:
                value = row["value"]

            dict_conn[row["param"]] = value

    context.sftp_session = sftp.WrapperSFTP(hostname=dict_conn['host'], port=int(dict_conn['port']),
                                            username=dict_conn['username'], password=dict_conn['password'])
    context.sftp_session.open_connection()

    context.func.add_formatter_evidence_json(dict_conn, "SFTP Connect")
    context.test_ftp_connect_data = dict_conn


@step(u"close SFTP connection")
def sftp_disconnect(context):
    """
    Close the SFTP connection
    :example
        Then close SFTP connection
    :
    :tag SFTP Connect:
    :param context:
    :return:
    """
    context.sftp_session.close_connection()


#######################################################################################################################
#                                                  SFTP Get Steps                                                      #
#######################################################################################################################


@step(u"download file '(?P<remote_file_path>.+)' from SFTP server in local file '(?P<local_file_path>.+)'")
def sftp_download_parameter(context, remote_file_path, local_file_path):
    """
    Download the file passed by parameter and save it in the local path and name also passed by parameter
    :example
        Given download file '/1/2021/03/07/photo.jpg' from SFTP server in local file 'download/aphoto_copy.jpg'

        Given download file '/1/2021/03/07/photo.jpg' from SFTP server in local file 'download/aphoto.jpg'
    :
    :tag SFTP Get Action:
    :param context:
    :param remote_file_path:
    :param local_file_path:
    :return context.test_sftp_get:
    """
    dict_evidence = {
        'local file path': local_file_path,
        'remote file path': remote_file_path
    }
    context.sftp_session.get_file(remote_path=remote_file_path, local_path=local_file_path)
    context.func.add_formatter_evidence_json(dict_evidence, "SFTP Download file")
    verification = files.is_file_exist(local_file_path)
    context.func.generate_table_evidence("Check if the file was downloaded correctly", value_expected=str(True),
                                         result_flag=str(verification))
    context.test_ftp_get = dict_evidence


@step(u"download file from SFTP server in local file")
def sftp_download_data_table(context):
    """
    Download the file using the path and remote file name and save it in a directory passed by parameter.
    Both the remote and local file path parameters must be passed through a data table.
    said data table will contain the parameter "remote_path" and the parameter "local_path"
    :example
            Given download file from SFTP server in local file
              | param       | value                   |
              | remote_path | /1/2021/03/07/image.jpg |
              | local_path  | download/image.jpg      |
    :
    :tag SFTP Get Action:
    :param context:
    :return context.test_ftp_get:
    """
    dict_conn = {}
    if context.table:
        for row in context.table:
            if context.func.is_contains_profile_re_var(row["value"]):
                value = context.func.get_unique_profile_re_var(row["value"], context.master_file_name_config)
            else:
                value = row["value"]

            dict_conn[row["param"]] = value

    dict_evidence = {
        'local file path': dict_conn['local_path'],
        'remote file path': dict_conn['remote_path']
    }
    context.sftp_session.get_file(remote_path=dict_conn['remote_path'], local_path=dict_conn['local_path'])
    context.func.add_formatter_evidence_json(dict_evidence, "SFTP Download file")
    context.test_ftp_get = dict_evidence

    verification = files.is_file_exist(dict_conn['local_path'])
    context.func.generate_table_evidence("Check if the file was downloaded correctly", value_expected=str(True),
                                         result_flag=str(verification))


@step(u"saves in the context variable a list of files in the remote directory '(?P<remote_path>.+)' from SFTP server")
def sftp_save_file_directory_list(context, remote_path):
    """
    saves a list of files of the remote directory in the context variable: context.sftp_list_files
     :example
        Given saves in the context variable a list of files in the remote directory '/remote/path'
    :
    :tag SFTP Get Action:
    :param context:
    :param remote_path:
    :return:
    """
    context.sftp_session.change_dir(remote_path)
    context.sftp_list_files = context.sftp_session.list_dir()
    dict_file = {
        'remote file path': remote_path,
        'files': context.sftp_list_files
    }
    context.func.add_formatter_evidence_json(dict_file, "SFTP File Directory")

    verification = context.sftp_list_files is not None
    context.func.generate_table_evidence("Check if the list file was saved correctly", value_expected=str(True),
                                         result_flag=str(verification))

#######################################################################################################################
#                                                  SFTP Put Steps                                                    #
#######################################################################################################################


@step(u"upload the file '(?P<local_file_path>.+)' to the SFTP server in the path '(?P<remote_file_path>.+)'")
def sftp_put_file(context, local_file_path, remote_file_path):
    """
    upload a file using the path and name of the file to the SFTP server, indicating
    the path and name of the remote file by parameterization.
    :example
        Given upload the file 'download/test.txt' to the SFTP server in the path '/1/2021/03/test.txt'
    :
    :tag SFTP Put Action:
    :param context:
    :param local_file_path:
    :param remote_file_path:
    :return context.test_ftp_put:
    """
    size = context.sftp_session.put_file(local_path=local_file_path, remote_path=remote_file_path)
    dict_evidence = {
        'local file path': local_file_path,
        'remote file path': remote_file_path,
        'size': str(size)
    }
    context.func.add_formatter_evidence_json(dict_evidence, "SFTP Upload file")
    context.test_ftp_put = dict_evidence
    verification = size is not None
    context.func.generate_table_evidence("Check if the file was uploaded correctly",
                                         value_expected=str(True), result_flag=str(verification))


@step(u"upload a file to the SFTP server")
def sftp_put_file_data_table(context):
    """
    Upload a file to the SFTP server using a data table
    The data table must have the header "param" and "value"
    the parameters for the column of "param" must be "local_path" and "remote_path" obligatorily
    For the column "value" must be paths with file name
    :example
        Given upload a file to the FTP server
          | param       | value                |
          | local_path  | download/test.txt    |
          | remote_path | /1/2021/03/test2.txt |
    :
    :tag SFTP Put Action:
    :param context:
    :return:
    """
    dict_conn = {}
    if context.table:
        for row in context.table:
            if context.func.is_contains_profile_re_var(row["value"]):
                value = context.func.get_unique_profile_re_var(row["value"], context.master_file_name_config)
            else:
                value = row["value"]

            dict_conn[row["param"]] = value

    size = context.sftp_session.put_file(local_path=dict_conn['local_path'], remote_path=dict_conn['remote_path'])
    dict_evidence = {
        'local file path': dict_conn['local_path'],
        'remote file path': dict_conn['remote_path'],
        'size': str(size)
    }
    context.func.add_formatter_evidence_json(dict_evidence, "SFTP Upload file")
    context.test_ftp_put = dict_evidence
    verification = size is not None
    context.func.generate_table_evidence("Check if the file was uploaded correctly",
                                         value_expected=str(True), result_flag=str(verification))


@step(u"upload multiple files to SFTP server")
def sftp_multiple_files(context):
    """
    Upload multiple files to the SFTP server using a data table
    The data table must have the header "local" and "remote"
    the parameters for the column of "remote" must be the remote file path
    the parameters for the column of "local" must be the local file path
    :example
        Given upload multiple files to SFTP server
          | local                | remote                |
          | download/test.txt    | download/test11.txt   |
          | download/weather.jpg | download/weather1.jpg |
    :
    :tag SFTP Put Action:
    :param context:
    :return context.sftp_put:
    """
    dict_files = {}
    file_count = 1
    if context.table:
        for row in context.table:
            dict_conn = {}
            if context.func.is_contains_profile_re_var(row["remote"]):
                value_remote = context.func.get_unique_profile_re_var(row["remote"], context.master_file_name_config)
            else:
                value_remote = row["remote"]
            if context.func.is_contains_profile_re_var(row["local"]):
                value_local = context.func.get_unique_profile_re_var(row["local"], context.master_file_name_config)
            else:
                value_local = row["local"]

            dict_conn['remote'] = value_remote
            dict_conn['local'] = value_local
            dict_files[f'file {file_count}'] = dict_conn
            file_count += 1

    verification = True
    error_msg = None
    for test_files in dict_files:
        try:
            paths = dict_files[test_files]
            context.sftp_session.put_file(paths['local'], paths['remote'])
        except Exception as ex:
            verification = False
            error_msg = ex

    context.func.add_formatter_evidence_json(dict_files, "FTP Upload Multiple Files")
    context.test_ftp_put = dict_files
    context.func.generate_table_evidence("Check if the files were uploaded correctly",
                                         value_expected=str(True), result_flag=str(verification),
                                         error_message=error_msg)
    if verification is not True:
        raise Exception(error_msg)

#######################################################################################################################
#                                              SFTP Actions Steps                                                      #
#######################################################################################################################


@step(u"go to directory '(?P<remote_path>.+)' from SFTP")
def sftp_go_to_directory(context, remote_path):
    """
    Change the current directory of the session to the SFTP server to the new directory passed by parameter
    It has the same functionality as the cd command
    :example
            Given go to directory '/1/2021'
            And go to directory '/2/2021'
    :
    :tag SFTP General Actions
    :param context:
    :param remote_path:
    :return:
    """
    current_path = context.sftp_session.get_current_dir()
    context.sftp_session.change_dir(remote_path)
    dict_evidence = {
        'current path': current_path,
        'remote_path': remote_path
    }
    context.func.add_formatter_evidence_json(dict_evidence, "SFTP Go to Directory")
    context.test_ftp_actions = dict_evidence
    verification = remote_path == remote_path
    context.func.generate_table_evidence("Check if directory was changed correctly",
                                         value_expected=str(remote_path), result_flag=str(verification))


@step(u"create directory '(?P<dir_name>.+)' from SFTP")
def sftp_create_dir(context, dir_name):
    """
    Create a directory in the remote path passed by parameter the new directory name
    :example
        Given create directory 'test'
    :
    :tag SFTP General Actions
    :param context:
    :param dir_name:
    :return context.sftp_actions:
    """
    context.sftp_session.create_dir(dir_name)
    dict_evidence = {
        'new_directory': dir_name
    }
    context.func.add_formatter_evidence_json(dict_evidence, "SFTP Create Directory")
    context.test_ftp_actions = dict_evidence
    verification = True
    context.func.generate_table_evidence("Verify that the directory was created correctly",
                                         value_expected=str(verification), result_flag=str(verification))


@step(u"create multiple directory in '(?P<remote_path>.+)' from SFTP")
def sftp_create_multi_dir(context, remote_path):
    """
    Create multiple directory in the remote path passed by parameter
    :example
       Given create multiple directory in 'test/test1/test2'
    :
    :tag SFTP General Actions
    :param context:
    :param remote_path:
    :return context.test_ftp_actions:
    """

    list_dir = remote_path.split('/')
    verification = True
    error_msg = None
    current_path = context.sftp_current_dir
    try:
        for directory in list_dir:
            context.sftp_session.create_dir(current_path + '/' + directory)
            context.sftp_session.change_dir(current_path + '/' + directory)
            current_path = current_path + '/' + directory
    except Exception as ex:
        verification = False
        error_msg = ex

    dict_evidence = {
        'new_directory': remote_path
    }
    context.func.add_formatter_evidence_json(dict_evidence, "SFTP Create Multiple Directory")
    context.test_ftp_actions = dict_evidence

    context.func.generate_table_evidence("Check if the files were uploaded correctly",
                                         value_expected=str(True), result_flag=str(verification),
                                         error_message=error_msg)
    if verification is not True:
        raise Exception(error_msg)


@step(u"delete file '(?P<remote_file_path>.+)' from SFTP")
def sftp_delete_file(context, remote_file_path):
    """
    Delete file in the remote path passed by parameter
    :example
       Given delete file '/1/2021/text.txt'
    :
    :tag SFTP General Actions
    :param context:
    :param remote_file_path:
    :return context.test_ftp_actions:
    """
    context.sftp_session.delete_file(remote_file_path)
    dict_evidence = {
        'delete_file': remote_file_path
    }
    context.func.add_formatter_evidence_json(dict_evidence, "SFTP Delete File")
    context.test_ftp_actions = dict_evidence
    verification = True
    context.func.generate_table_evidence("Check if the files were deleted correctly",
                                         value_expected=str(True), result_flag=str(verification))


@step(u"saves in the context variable the current directory path from SFTP")
def sftp_save_current_dir_context(context):
    """
    Saves in the context variable "context.sftp_current_dir" the current directory path of the SFTP server
    :example
        Given saves in the context variable the current directory path
    :
    :tag SFTP General Actions
    :param context:
    :return context.sftp_current_dir:
    """
    context.sftp_current_dir = context.sftp_session.get_current_dir()
    dict_file = {
        'current_directory_path': context.sftp_current_dir
    }
    context.func.add_formatter_evidence_json(dict_file, "SFTP Save Current Directory Path")
    verification = context.sftp_current_dir is not None
    context.func.generate_table_evidence("Verify that the current directory was saved correctly",
                                         value_expected=str(True), result_flag=str(verification))


@step(u"(rename|move) the remote file '(?P<remote_file_path>.+)' to '(?P<remote_file_path_to>.+)' from SFTP")
def ftp_rename_move_file(context, selection, remote_file_path, remote_file_path_to):
    """
    Move or rename a file using its source path and destination path
    :example
        Given rename the remote file '/1/2021/image.jpg' to '/1/2021/rename_image.jpg'

        Given move the remote file '/1/2021/image.jpg' to '/other/path/image.jpg'

        Given move the remote file '/1/2021/image.jpg' to '/other/path/rename_image.jpg'
    :
    :tag SFTP General Actions
    :param context:
    :param selection:
    :param remote_file_path:
    :param remote_file_path_to:
    :return context.test_ftp_rename_move:
    """
    context.sftp_session.rename(remote_file_path, remote_file_path_to)
    dict_file = {
        'remote_file_name_to': remote_file_path_to,
        'remote_file_name_from': remote_file_path
    }
    context.func.add_formatter_evidence_json(dict_file, f"SFTP {selection} File")
    context.test_ftp_rename_move = dict_file
    verification = True
    context.func.generate_table_evidence("Verify that the file was moved and renamed correctly",
                                         value_expected=str(True), result_flag=str(verification))


@step(u"saves in the context variable the current SFTP server session")
def sftp_save_current_session_context(context):
    """
    Saves in the context variable "context.sftp_current_session" the current SFTP server session
    :example
        Given saves in the context variable the current SFTP server session
    :
    :tag SFTP General Actions
    :param context:
    :return context.sftp_current_session:
    """
    context.sftp_current_session = context.sftp_session.get_session()
    dict_file = {
        'current_session': str(context.sftp_current_session)
    }
    context.func.add_formatter_evidence_json(dict_file, "SFTP Save Current Session")
    verification = context.sftp_current_session is not None
    context.func.generate_table_evidence("Verify that the current session was saved correctly",
                                         value_expected=str(True), result_flag=str(verification))
