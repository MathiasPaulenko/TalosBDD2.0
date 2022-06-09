import re


def re_formatter(escaped_arg):
    def regex_escaped(obj, *args):
        esc = [isinstance(arg, RegExCompose) and arg.reg or re.escape(str(arg)) for arg in args]
        return escaped_arg(obj, *esc)

    return regex_escaped


class RegExCompose(object):
    def __init__(self):
        self.reg = []
        self.modifiers = {'A': 0, 'I': 0, 'L': 0, 'M': 0, 'S': 0, 'U': 0, 'X': 0}

    def __getattr__(self, attr):
        regex = self.regex()
        return getattr(regex, attr)

    def __str__(self):
        return "".join(self.reg)

    def add(self, value):
        if isinstance(value, list):
            self.reg.extend(value)
        else:
            self.reg.append(value)
        return self

    def regex(self):
        return re.compile(str(self), self.modifiers["I"] | self.modifiers["M"] | self.modifiers["A"])

    def custom_flag(self, flag=None):
        return re.compile(str(self), self.modifiers[flag.upper()]) if flag else None

    def expression(self):
        return str(self)

    def anything(self):
        return self.add("(.*)")

    @re_formatter
    def anything_except(self, value):
        return self.add("([^{value}]*)".format(value=value))

    def end_of_line(self):
        return self.add("$")

    @re_formatter
    def maybe(self, value):
        return self.add("({value})?".format(value=value))

    def start_of_line(self):
        return self.add("^")

    @re_formatter
    def find(self, value):
        return self.add("({value})".format(value=value))

    @re_formatter
    def format_occurrence(self, number):
        if isinstance(number, int):
            return "{number:d}".format(number=number)
        elif isinstance(number, tuple) or isinstance(number, list):
            return "{min:d},{max:d}".format(min=number[0], max=number[1])

    @re_formatter
    def occurrence(self, num):
        return self.add("{" + self.format_occurrence(num) + "}")

    @re_formatter
    def any(self, value):
        return self.add("([{value}])".format(value=value))

    def line_break(self):
        return self.add(r"(\n|(\r\n))")

    @re_formatter
    def dictionary(self, *args):
        rang = [args[i: i + 2] for i in range(0, len(args), 2)]
        return self.add("([{arg}])".format(arg="".join(["-".join(i) for i in rang])))

    def tabulator(self):
        return self.add(r"\t")

    def alphanumeric(self):
        return self.add(r"(\w+)")

    def no_alphanumeric(self):
        return self.add(r"(\W+)")

    def digit(self):
        return self.add(r"(\d+)")

    def no_digit(self):
        return self.add(r"(\D+)")

    def white_spaces(self):
        return self.add(r"(\s+)")

    def no_white_spaces(self):
        return self.add(r"(\S+)")

    def anyone(self, value=None):
        self.add("|")
        return self.find(value) if value else self

    def find_all(self, expression, string):
        return self.findall(expression, string)

    def splitter(self, delimiter, string):
        return self.split(delimiter, string) if delimiter else None

    def search_first(self, expression, string):
        return self.search(expression, string)

    def replace(self, string, repl):
        return self.sub(repl, string)

    def with_ascii(self, value=False):
        self.modifiers["A"] = re.A if value else 0
        return self

    def with_any_case(self, value=False):
        self.modifiers["I"] = re.I if value else 0
        return self

    def locale_dependent(self, value=False):
        self.modifiers["L"] = re.L if value else 0
        return self

    def multiline(self, value=False):
        self.modifiers["M"] = re.M if value else 0
        return self

    def all_match(self, value=False):
        self.modifiers["S"] = re.S if value else 0
        return self

    def with_unicode(self, value=False):
        self.modifiers["U"] = re.U if value else 0
        return self

    def verbose(self, value=False):
        self.modifiers["X"] = re.X if value else 0
        return self
