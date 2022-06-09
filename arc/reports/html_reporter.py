import os

from junit2htmlreport import runner as junit2html_runner

from arc.settings import settings

REPORTS_HOME = os.path.join(settings.OUTPUT_PATH, 'reports/html') + os.sep


def make_html_reports(path=REPORTS_HOME):
    """
    It converts junit reports into html report and return output paths
    :param path:
    :return:
    """
    if os.path.isdir(path):
        xmls = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and f[-4:] == '.xml']
        output = []
        for r in xmls:
            file = path + r
            new_file = path + r[:-4] + '.html'
            junit2html_runner.run([file, new_file])
            output.append(new_file)
        return output

    else:
        os.stat(path)
        new_path = path[:-4] + '.html'
        junit2html_runner.run([path, new_path])
        return new_path


if __name__ == '__main__':
    make_html_reports()
