import pandas as pd
import os

from arc.contrib.tools.excel import ExcelWrapper

dirname = os.path.dirname
ROOT_PATH = dirname(dirname(dirname(__file__)))


class CSVWrapper(ExcelWrapper):

    def __init__(self, route_filename=None):
        self.engine = None
        if route_filename is not None:
            route_filename = route_filename.replace(os.sep, '/')
            splitted = route_filename.rsplit('/', 1)

            self.route = os.path.join(ROOT_PATH, splitted[0]+'/') if len(splitted) > 1 else ROOT_PATH + '/'
            self.filename = splitted[1] if len(splitted) > 1 else splitted[0]
            self.file = self._read_file()
            self.current_sheet = self.filename
            self.sheets = {self.filename: self.file}
            self.headers = self._get_headers()

    def set_sheet_header(self, header, sheet_name=None):
        """
            This method set the selected row as the header of the file.
            The parameter header must be an int higher than 0 and None if you don't want to use any header.
        :param header: int
        :param sheet_name: str
        """
        sheet = pd.read_csv(
            self.route + self.filename,
            delimiter=";",
            header=None if header is None else header-1,
            engine=self.engine
        )
        self.sheets[self.current_sheet] = sheet
        self.headers[self.current_sheet] = sheet.head()

    def _read_file(self):
        """
            Read the file and return a dataframe
        """
        # delimiter of spanish csv
        return pd.read_csv(self.route + self.filename, delimiter=";", header=None)

    def __str__(self):
        rows, columns = self.file.shape
        return f" {self.filename}, rows={rows}, columns={columns}"

    def save(self):
        """
            Save the CSV file.
        """
        sheet = self.sheets[self.current_sheet]
        sheet_header = True if self.headers[self.current_sheet] is not None else False
        sheet.to_csv(self.route + self.filename, index=False, header=sheet_header, sep=';')
