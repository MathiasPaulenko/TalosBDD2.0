import os
import re
import pandas as pd

OPENPYXL_ENGINE = 'openpyxl'
dirname = os.path.dirname
ROOT_PATH = dirname(dirname(dirname(__file__)))


class ExcelWrapper:
    def __init__(self, route_filename=None):
        """
        :param filename:
        """
        self.engine = OPENPYXL_ENGINE
        if route_filename is not None:
            splitted = route_filename.rsplit('/', 1)

            self.route = os.path.join(ROOT_PATH, splitted[0] + '/') if len(splitted) > 1 else ROOT_PATH + '/'
            self.filename = splitted[1] if len(splitted) > 1 else splitted[0]
            self.file = self._read_file()
            self.current_sheet = self.file.sheet_names[0]
            self.sheets = self._get_sheets()
            self.headers = self._get_headers()

    def _read_file(self):
        return pd.ExcelFile(self.route + self.filename, engine=self.engine)

    def _get_sheets(self):
        sheets = {}
        for sheet_name in self.file.sheet_names:
            sheet = pd.read_excel(self.route + self.filename, sheet_name, header=None, engine=self.engine)
            sheets[sheet_name] = sheet
        return sheets

    def _get_headers(self):
        headers = {}
        for sheet_name in self.sheets.keys():
            headers[sheet_name] = None
        return headers

    def __str__(self):
        rows, columns = self.sheets[self.current_sheet].shape
        return f" {self.filename}, sheet={self.current_sheet}, rows={rows}, columns={columns}"

    # Should we (1) return another object or (2) just re-read the file?
    # Here we choose option (2)
    def set_current_sheet(self, sheet_name):
        self.current_sheet = sheet_name

    def set_sheet_header(self, header, sheet_name=None):
        sheet_name = self.current_sheet if sheet_name is None else sheet_name
        sheet = pd.read_excel(
            self.route + self.filename,
            sheet_name,
            header=None if header is None else header-1,
            engine=self.engine
        )
        self.sheets[sheet_name] = sheet
        self.headers[sheet_name] = sheet.head()

    def current_sheet_to_json(self):
        """
            Return a json object of the current sheet  .
        """
        return self.sheets[self.current_sheet].to_json()

    def all_sheets_to_json(self):
        """
            Return a json objects with all the sheets.
        """
        sheets = {}
        for sheet_name, sheet in self.sheets.items():
            sheets[sheet_name] = sheet.to_json()
        return sheets

    def __read_cell(self, row_from_zero, column_from_zero, sheet_name=None):
        sheet = self.sheets[sheet_name]
        return sheet.iloc[row_from_zero, column_from_zero]

    @staticmethod
    def __convert_row(row_number):
        return row_number - 1

    @staticmethod
    def __letter_number(letter):
        return ord(letter) - ord('A')

    def __convert_column_letter(self, column_letter):
        """
            Given a column letter return an integer representing the column position
        :param column_letter: str
        """
        letter_number = 0
        for number_of_letter, letter in enumerate(column_letter):
            letter_number += (
                    self.__letter_number(letter) +
                    (ord('Z') - ord('A') + 1) * number_of_letter
            )
        return letter_number

    def __convert_to_column(self, column_type, sheet_name=None):
        column = None
        header = self.headers[sheet_name]
        if isinstance(column_type, str):
            if header is not None and column_type in header:
                column = [position for position, header in enumerate(header) if header == column_type][0]
            else:
                column = self.__convert_column_letter(column_type)
        elif isinstance(column_type, int):
            column = column_type - 1
        return column

    def read_cell(self, row_number, column_type, sheet_name=None):
        """
            Given a row int and a str or int column return the value of the selected cell.
            Optionally if you want to read a cell from another sheet without changing your actual sheet you can
            pass the parameter sheet_name with the sheet_name
        :param row_number: int
        :param column_type: int/str
        :param sheet_name: str
        """
        sheet_name = self.current_sheet if sheet_name is None else sheet_name
        return self.__read_cell(
            self.__convert_row(row_number),
            self.__convert_to_column(column_type, sheet_name),
            sheet_name
        )

    def read_row(self, row_number, sheet_name=None):
        """
            Given a row int return all the values of the selected row
            Optionally if you want to read a row from another sheet without changing your actual sheet you can
            pass the parameter sheet_name with the sheet_name
        :param sheet_name: str
        :param row_number: int
        """
        sheet_name = self.current_sheet if sheet_name is None else sheet_name
        row = []
        _, columns = self.sheets[sheet_name].shape
        for column in range(columns):
            row.append(self.__read_cell(
                self.__convert_row(row_number), column, sheet_name),
            )
        return row

    def read_column(self, column_type, sheet_name=None):
        """
            Given a column int or str return all the values of the selected column
            Optionally if you want to read a column from another sheet without changing your actual sheet you can
            pass the parameter sheet_name with the sheet_name
        :param sheet_name: str
        :param column_type: int/str
        """
        sheet_name = self.current_sheet if sheet_name is None else sheet_name
        column_number = self.__convert_to_column(column_type, sheet_name)
        column = []
        rows, _ = self.sheets[sheet_name].shape
        for row in range(rows):
            column.append(
                self.__read_cell(
                    row, column_number, sheet_name
                )
            )
        return column

    def read_range(self, range_string, sheet_name=None):
        """
            This method read a range of cells.
            Optionally if you want read another range sheet without changing your actual sheet you can
            pass the parameter sheet_name with the sheet_name
        :param range_string: str
        :param sheet_name: str
        """
        sheet_name = self.current_sheet if sheet_name is None else sheet_name
        try:
            # TODO if con el separador para rendimiento correcto // levantar exception propia con el tipo de formato valido
            # get the cells that are indicated by the pair of cells from:to
            pattern_spanish_letters = r'[A-Z]*'
            string_from, string_to = range_string.upper().split(":")
            column_letter_from = re.search(pattern_spanish_letters, string_from)[0]
            row_from = int(string_from.replace(column_letter_from, ""))
            column_letter_to = re.search(pattern_spanish_letters, string_to)[0]
            row_to = int(string_to.replace(column_letter_to, ""))
        except ValueError as err:  # misformatted range_string, raise
            print("Unsupported range: ", err)
            raise
        # TODO Refactor range
        # return matrix as list of lists
        matrix = []
        for row_number in range(self.__convert_row(row_from),
                                self.__convert_row(row_to) + 1):
            column = []
            for column_number in range(
                    self.__convert_to_column(column_letter_from, sheet_name),
                    self.__convert_to_column(column_letter_to, sheet_name) + 1
            ):
                cell = self.__read_cell(row_number, column_number, sheet_name)
                column.append(cell)
            matrix.append(column)
        return matrix

    def read_all(self, sheet_name=None):
        """
            This function read the file and return a list of lists
            Optionally if you want read another sheet without changing your actual sheet you can
            pass the parameter sheet_name with the sheet_name
            :param sheet_name: str
        """
        # return matrix as list of lists
        sheet_name = self.current_sheet if sheet_name is None else sheet_name
        matrix = []
        rows, columns = self.sheets[sheet_name].shape
        # read all rows
        for row_number in range(rows):
            column = []
            for column_number in range(columns):
                cell = self.__read_cell(row_number, column_number, sheet_name=sheet_name)
                column.append(cell)
            matrix.append(column)
        return matrix

    def write_cell(self, row_number, column_type, new_value, sheet_name=None):
        """
            This function update the cell value given a row_number and a column_type.
            column_type can be an integer or a string representing the column.
            Optionally if you want to write the cell from another sheet without changing your actual sheet you can
            pass the parameter sheet_name with the sheet_name
        :param row_number: int
        :param column_type: int/str
        :param new_value: any
        :param sheet_name:str
        """
        sheet_name = self.current_sheet if sheet_name is None else sheet_name
        row_number = self.__convert_row(row_number)
        column_type = self.__convert_to_column(column_type, sheet_name)
        self.sheets[sheet_name].iloc[row_number, column_type] = new_value

    def write_row(self, row_number, values, sheet_name=None):
        """
            This function update a complete row with the passed values as list.
            Optionally if you want to write the row from another sheet without changing your actual sheet you can
            pass the parameter sheet_name with the sheet_name
        :param row_number: int
        :param values: list
        :param sheet_name: str
        """
        sheet_name = self.current_sheet if sheet_name is None else sheet_name
        row_number = self.__convert_row(row_number)
        column_type = 0
        for value in values:
            self.sheets[sheet_name].iloc[row_number, column_type] = value
            column_type += 1

    def write_column(self, column_type, values, sheet_name=None):
        """
            This function update a complete column with the passed values as list.
            Optionally if you want to write the column from another sheet without changing your actual sheet you can
            pass the parameter sheet_name with the sheet_name
        :param column_type: int/str
        :param values: list
        :param sheet_name: str
        """
        sheet_name = self.current_sheet if sheet_name is None else sheet_name
        column_type = self.__convert_to_column(column_type, sheet_name)
        row_number = 0
        for value in values:
            self.sheets[sheet_name].iloc[row_number, column_type] = value
            row_number += 1

    def delete_cell(self, row_number, column_type, sheet_name=None):
        """
            This method clear
            Optionally if you want to remove the cell from another sheet without changing your actual sheet you can
            pass the parameter sheet_name with the sheet_name
        :param row_number: int
        :param column_type: int/str
        :param sheet_name: str
        :return:
        :rtype:
        """
        sheet_name = self.current_sheet if sheet_name is None else sheet_name
        self.write_cell(row_number, column_type, sheet_name)

    def delete_rows(self, row_numbers, sheet_name=None):
        """
            This method remove a complete row or rows given a row index
            Optionally if you want to remove the row from another sheet without changing your actual sheet you can
            pass the parameter sheet_name with the sheet_name
        :param row_numbers: int/list
        :param sheet_name:  str
        """
        sheet_name = self.current_sheet if sheet_name is None else sheet_name
        if type(row_numbers) == list:
            _row_numbers = [self.__convert_row(row) for row in row_numbers]
        else:
            _row_numbers = row_numbers
        self.sheets[sheet_name].drop(_row_numbers)

    def delete_columns(self, column_types, sheet_name=None):
        """
            This method remove a complete column or columns given a column index or names if you are using headers
            Optionally if you want to remove the column from another sheet without changing your actual sheet you can
            pass the parameter sheet_name with the sheet_name
        :param column_types: int/str/list
        :param sheet_name: str
        """
        sheet_name = self.current_sheet if sheet_name is None else sheet_name
        if type(column_types) == list:
            _column_types = [self.__convert_to_column(column_type) for column_type in column_types]
        else:
            _column_types = column_types
        self.sheets[sheet_name].drop(columns=_column_types)

    def save(self):
        """
            Save the Excel file.
        """

        writer = pd.ExcelWriter(self.route + self.filename, engine=self.engine)

        for sheet_name, sheet in self.sheets.items():
            sheet_header = True if self.headers[sheet_name] is not None else False
            sheet.to_excel(writer, sheet_name=sheet_name, index=False, header=sheet_header)
        writer.save()

