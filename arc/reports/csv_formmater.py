import csv
import datetime
import os
from arc.contrib.tools import formatters
from settings import settings

EXCEL_HOME = os.path.join(settings.SETTINGS_PATH, 'talosbdd-alm-config.csv')


def is_empty(final_data):
    if final_data:
        return False
    else:
        return True


class CSVFormatter:
    feature_name = ''
    tc_scenario_name = ""
    results = []
    csv_data = {}
    final_data = {}
    scenario = ''
    settings = None

    def __init__(self):
        self.csv_data = self.get_csv_data()
        self.settings = settings

    @staticmethod
    def get_csv_data():
        results = []
        with open(EXCEL_HOME) as File:
            reader = csv.reader(File, delimiter=';', quotechar=',',
                                quoting=csv.QUOTE_MINIMAL)
            for row in reader:
                results.append(row)

        alm = []
        for s in results[0]:
            alm.append(s)

        datas = []
        for x in range(1, results.__len__()):
            almvalues = []
            for s in results[x]:
                almvalues.append(s)
            dictionary = {}
            for y in range(0, len(results[x])):
                dictionary[alm[y]] = almvalues[y]
            datas.append(dictionary)
        return datas

    def format_feature_name(self, scenario):
        msg_modify = scenario.feature.filename.replace("features/", "")
        msg_modify = msg_modify.replace(".feature", "")
        self.scenario = scenario
        self.feature_name = msg_modify
        return msg_modify

    def set_scenario_data(self, scenario):
        self.tc_scenario_name = str(scenario.name).strip()

    def get_csv_heading(self):
        return self.csv_data[0]

    def alm_option_controller(self):
        try:
            base = self.csv_data[0]
            if self.csv_data.__len__() == 1:
                base['feature-file'] = self.feature_name
                base['scenario'] = self.tc_scenario_name
                self.final_data = base

            if self.csv_data.__len__() > 1:
                for option in self.csv_data:
                    if option.get('feature-file') == '':
                        base['feature-file'] = self.feature_name
                        base['scenario'] = self.tc_scenario_name
                        for index in option:
                            if option.get(index) == '':
                                self.final_data[index] = base[index]
                            else:
                                self.final_data[index] = option[index]
                    elif option.get('feature-file') == self.feature_name and option.get('scenario') == '':
                        base['scenario'] = self.tc_scenario_name
                        for index in option:
                            if option.get(index) == '':
                                self.final_data[index] = base[index]
                            else:
                                self.final_data[index] = option[index]
                    elif option.get('feature-file') == self.feature_name and option.get(
                            'scenario') == self.tc_scenario_name:
                        for index in option:
                            if option.get(index) == '':
                                self.final_data[index] = base[index]
                            else:
                                self.final_data[index] = option[index]

        except (Exception,):
            print('Please, fill in the ALM configuration csv properly.')

        return self.final_data

    def csv_con_necesary_data(self):
        cd = datetime.datetime.now()
        alm_data = self.alm_option_controller()
        for index in alm_data:
            if index == 'tc-path':
                alm_data[index] = alm_data[index] + '/' + str(self.feature_name)
            if index == 'tc-descrip':
                if self.scenario.description:
                    text = formatters.replace_chars(str(self._parse_list_to_string(self.scenario.description)))
                else:
                    text = formatters.replace_chars(str(self.scenario.name))
                    description = text
                    for step in self.scenario.all_steps:
                        description = description + '\n' + str(step)
                    text = formatters.replace_chars(str(description))
                alm_data[index] = text
            if index == 'tc-name' and alm_data[index] == '':
                text = formatters.replace_chars(str(self.tc_scenario_name))
                alm_data[index] = text
            if index == 'ts-name' and alm_data[index] == '':
                feature_name = self._format_feature_path(self.feature_name)
                if self.settings.PYTALOS_ALM['match_alm_execution']:
                    alm_data[index] = str(feature_name)
                else:
                    alm_data[index] = str(feature_name) + '_' + str(cd.day) \
                                      + '-' + str(cd.month) + '-' + str(cd.year)
            if index == 'ts-descrip' and alm_data[index] == '':
                text = formatters.replace_chars(str(self.scenario.feature.description))
                alm_data[index] = text
            if index == 'ts-path' and alm_data[index] == '':
                alm_data[index] = alm_data['tc-path']

        return alm_data

    @staticmethod
    def _format_feature_path(feature_path):
        if '/' in feature_path:
            feature_path = str(feature_path).split("/")[-1]
        if '\\' in feature_path:
            feature_path = str(feature_path).split("\\")[-1]
        return feature_path

    @staticmethod
    def _parse_list_to_string(ini_list):
        return "\n ".join(ini_list)

    def get_final_data(self):
        final_data_form = []
        aux_dict_alm = {}
        aux_dict_tc = {}
        aux_dict_ts = {}
        aux_dict_other = {}
        alm_data = self.csv_con_necesary_data()

        for row in alm_data:
            if row.startswith("alm-"):
                aux_dict_alm[row] = alm_data[row]
            elif row.startswith("tc-"):
                aux_dict_tc[row] = alm_data[row]
            elif row.startswith("ts-"):
                aux_dict_ts[row] = alm_data[row]
            else:
                aux_dict_other[row] = alm_data[row]

        final_data_form.append(aux_dict_other)
        final_data_form.append(aux_dict_alm)
        final_data_form.append(aux_dict_tc)
        final_data_form.append(aux_dict_ts)

        return final_data_form
