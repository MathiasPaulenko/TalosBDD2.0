import os


def enabled_proxy(http, https):
    os.environ["HTTP_PROXY"] = str(http)
    os.environ["HTTPS_PROXY"] = str(https)
