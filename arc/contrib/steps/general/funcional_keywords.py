"""
Funcional Default Keywords
Default steps for use in Gherkin features.
In each step there is the documentation of what it is for and how to use it, as well as an example.
In some steps, not only is the desired operation performed, but it also adds extra information to the Word evidence.

List of steps:
######################################################################################################################

## Mail Steps:
login to the mail {mail} with password {password} and SMTP server {server}
login to the mail
logout mail
get the last {mails_num>} emails
send new mail
delete mails

"""

from distutils import util
from behave import use_step_matcher, step

from arc.contrib.tools.mail import Mail

use_step_matcher("re")


#######################################################################################################################
#                                                  Mail Steps                                                         #
#######################################################################################################################
@step(u"login to the mail '(?P<mail>.+)' with password '(?P<password>.+)' and SMTP server '(?P<server>.+)'")
def login_mail_password_server(context, mail, password, server):
    """
    This step allows you to connect to an email using the email address, password and SMTP server as parameters.
    Allows use of template variable
    Save the email instance in the context variable context.mail
    :example
       Given login to the mail 'mail@outlook.com' with password 'abc123' and SMTP server 'smtp-mail.outlook.com'
    :
    :tag Mail Login:
    :param context:
    :param mail:
    :param password:
    :param server:
    :return context.mail:
    """
    if context.func.is_contains_profile_re_var(mail):
        mail = context.func.get_formatter_multiple_re_var(mail, context.master_file_name_config)
    if context.func.is_contains_profile_re_var(password):
        password = context.func.get_formatter_multiple_re_var(password, context.master_file_name_config)
    if context.func.is_contains_profile_re_var(mail):
        password = context.func.get_formatter_multiple_re_var(password, context.master_file_name_config)

    context.mail = Mail(mail, password, server)
    dict_evidence = {
        'mail': mail,
        'password': password,
        'server': server
    }
    context.func.add_formatter_evidence_json(dict_evidence, "Mail Login")


@step(u"login to the mail")
def login_data_table(context):
    """
    This step allows you to connect to an email using the email address, password and SMTP server in a data table.
    Allows use of template variable
    Save the email instance in the context variable context.mail
    :example
        Given login to the mail
          | param    | value                    |
          | mail     | mail@outlook.com         |
          | password | abc123                   |
          | server   | smtp-mail.outlook.com    |
    :
    :tag Mail Login:
    :param context:
    :return context.mail:
    """
    dict_conn = {}
    if context.table:
        for row in context.table:
            if context.func.is_contains_profile_re_var(row["value"]):
                value = context.func.get_formatter_multiple_re_var(row["value"], context.master_file_name_config)
            else:
                value = row["value"]

            dict_conn[row["param"]] = value

    mail = dict_conn['mail']
    password = dict_conn['password']
    server = dict_conn['server']
    context.mail = Mail(mail, password, server)
    context.func.add_formatter_evidence_json(dict_conn, "Mail Login")


@step(u"logout mail")
def delete_mails(context):
    """
    This step closes the session of the mail instance.
    :example
        Then logout mail
    :
    :tag Mail Logout:
    :param context:
    :return:
    """
    context.mail.logout()


@step(u"get the last '(?P<mails_num>.+)' emails")
def get_last_mails(context, mails_num):
    """
    This step allows you to get emails from the mail instance.
    Configuration data is passed through a Gherkin data table.
    The email number that we want to obtain is passed by parameter. This will return a dictionary list of
    the last n mails. The dictionary keys are "subject", "from" and "body".
    The parameter must be an integer.
    The list of dictionaries will be saved in the context variable context.test_mails
    :example
        Given get the last '1' emails

        When get the last '5' emails
    :
    :tag Mail Transaction:
    :param context:
    :param mails_num:
    :return context.test_mails:
    """
    try:
        mails_num = int(mails_num)
    except (Exception,):
        raise Exception("The get value of the last mails must be an integer")

    context.test_mails = context.mail.get_mail(mails_num=mails_num)
    dict_evidence = {}
    cont = 1
    for mail in context.test_mails:
        dict_evidence[f'mail {cont}'] = mail
        cont += 1
    context.func.add_formatter_evidence_json(dict_evidence, "Emails obtained")


@step(u"send new mail")
def send_new_mail(context):
    """
    This step will send an email with the data provided in a Gherkin data table
    The data table must have the parameters "to", "subject", "msg" being all these mandatory
    Optionally, the file parameter can be used to attach a file passing it the relative path of the file
    Allows you to send html or plain text, also attach any type of file. Template variable can be used
    :example
       When send new mail
          | param   | value                                     |
          | to      | test@outlook.es                           |
          | subject | Test                                      |
          | msg     | This is another one test <b>talosbdd!</b> |

        When send new mail
          | param   | value                                     |
          | to      | test@outlook.es                           |
          | subject | Test                                      |
          | msg     | This is another one test <b>talosbdd!</b> |
          | file    | files/text.txt                            |
    :
    :tag Mail Transaction:
    :param context:
    :return:
    """
    dict_conn = {}
    if context.table:
        for row in context.table:
            if context.func.is_contains_profile_re_var(row["value"]):
                value = context.func.get_formatter_multiple_re_var(row["value"], context.master_file_name_config)
            else:
                value = row["value"]

            dict_conn[row["param"]] = value

    to = dict_conn['to']
    subject = dict_conn['subject']
    msg = dict_conn['msg']

    file = []
    if 'file' in dict_conn.keys():
        file.append(dict_conn['file'])
    else:
        file = None

    context.mail.send_mail(to, subject, msg, files_to_send=file)
    context.func.add_formatter_evidence_json(dict_conn, "New Mail Sent")


@step(u"delete mails")
def delete_mails(context):
    """
    This step deletes emails by passing them a filter search passed through a data table
    The "search" parameter is mandatory and must contain the value of the search filter
    The "save_mail_deleted" parameter is optional, and must be True or False
    If the "save_mail_deleted" parameter is used, the emails that have been deleted will be saved
    in the context variable context.test_deleted_mails as a list with the subject of the email removed
    :example
        Then delete mails
          | param             | value                  |
          | search            | FROM "text@outlook.es" |
          | save_mail_deleted | False                  |

        Then delete mails
          | param             | value                  |
          | search            | SINCE "01-JAN-2020"    |
          | save_mail_deleted | True                   |

        Then delete mails
          | param             | value  |
          | search            | ALL    |

    :
    :tag Mail Transaction:
    :param context:
    :return context.test_deleted_mails:
    """
    dict_evidence = {}
    if context.table:
        for row in context.table:
            if context.func.is_contains_profile_re_var(row["value"]):
                value = context.func.get_formatter_multiple_re_var(row["value"], context.master_file_name_config)
            else:
                value = row["value"]

            dict_evidence[row["param"]] = value

    search = dict_evidence['search']
    if 'save_mail_deleted' in dict_evidence.keys():
        try:
            save_mail_deleted = bool(util.strtobool(dict_evidence['save_mail_deleted']))
        except Exception:
            raise Exception("The save_mail_deleted value must be a boolean")
    else:
        save_mail_deleted = False

    print(save_mail_deleted)
    mails_deleted = context.mail.delete_email(search, return_mail_deleted=save_mail_deleted)
    if mails_deleted is True:
        context.test_deleted_mails = mails_deleted
        count = 1
        dict_evidence['Deleted emails'] = {}
        for mails in mails_deleted:
            dict_evidence['Deleted emails'][f'mail {count}'] = str(mails)
            count += 1
    context.func.add_formatter_evidence_json(dict_evidence, "Deleted emails")
