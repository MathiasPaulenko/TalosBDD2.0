import os
from pathlib import Path

""" PyTalos configurations """
# Project configurations
BASE_PATH = Path(__file__).absolute().parent.parent
SETTINGS_PATH = os.path.join(BASE_PATH, 'settings')
OUTPUT_PATH = os.path.join(BASE_PATH, 'output')

# Proxy configuration
PROXY = {
    'http_proxy': '',
    'https_proxy': ''
}

# Project and general configuration
PYTALOS_GENERAL = {
    'download_path': "path",
    'auto_generate_output_dir': True,
    'auto_generate_test_dir': True,
    'update_driver': {
        'enabled_update': False,
        'enable_proxy': False,
        'proxy': PROXY
    }
}

# Run configuration
PYTALOS_RUN = {
    'delete_old_reports': True,
    'close_webdriver': True,
    'close_host': True,
    'continue_after_failed_step': False,
    'execution_proxy': {
        'enabled': False,
        'proxy': PROXY
    },

}

# Reports configurations
PYTALOS_REPORTS = {
    'generate_html': True,
    'generate_simple_html': True,
    'generate_docx': True,
    'generate_txt': True,
    'generate_screenshot': True,
    'generate_extra_reports': True,

}

# Profile datas configurations
PYTALOS_PROFILES = {
    'environment': 'cer',
    'master_file': 'master',
    'locale_fake_data': 'es_ES',
    'language': 'es'

}

# Step catalog configurations
PYTALOS_CATALOG = {
    'update_step_catalog': True,
    'excel_file_name': 'catalog',
    'steps': {
        'user_steps': False,
        'default_api': True,
        'default_web': True,
        'default_functional': True,
        'default_data': True,
        'default_ftp': True,
    }
}

""" Integrations """
# MF ALM integration configurations
PYTALOS_ALM = {
    'post_to_alm': False,
    'generate_json': True,
    'match_alm_execution': False,
    'alm3_properties': False,
}

# Jira integration configuration
PYTALOS_JIRA = {
    'post_to_jira': False,
    'username': 'user',
    'password': 'password',
    'base_url': 'https://jira.alm.europe.cloudcenter.corp',
    'report': {
        'comment_execution': True,
        'comment_scenarios': True,
        'upload_doc_evidence': True,
        'upload_txt_evidence': True,
        'upload_html_evidence': True,
    }
}

""" Behave configurations """
# BEHAVE configuration
BEHAVE = {
    'color': True,
    'junit': True,
    'default_format': 'pretty',
    'show_skipped': False,
    'show_multiline': True,
    'stdout_capture': False,
    'stderr_capture': False,
    'log_capture': True,
    'logging_level': 'INFO',
    'logging_clear_handlers': True,
    'summary': True,
    'show_source': True,
    'show_timings': True,
    'verbose': False,

}

""" BD Configurations"""
# SQLite configuration
SQLITE = {
    'enabled': False,
    'sqlite_home': os.path.join(BASE_PATH, 'db.sqlite3')
}

# Behave init file path configuration
# BEHAVE_INIT_PATH = os.path.join(BASE_PATH, 'settings') + os.sep
