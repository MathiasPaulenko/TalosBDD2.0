"""
python pytalos\integrations\cucumber.py -i output\reports\report_json_pretty.json -o output\reports\cucumber_json.json
"""
import os
import sys
import json
import getopt
import logging
from pathlib import Path
from pprint import pprint

_name = "cucumber_convert"
_debug = logging.WARNING

BASE_PATH = Path(__file__).absolute().parent.parent.parent
OUTPUT_PATH = os.path.join(BASE_PATH, 'output')
dir_logs = os.path.join(OUTPUT_PATH, 'logs')

# Logging
logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-10.10s]  %(message)s")
shortFormatter = logging.Formatter("[%(levelname)-8.8s]  %(message)s")
log = logging.getLogger()
log.setLevel(_debug)
fileHandler = logging.FileHandler(dir_logs + os.sep + 'cucumber_convert.log')
fileHandler.setFormatter(logFormatter)
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(shortFormatter)
log.addHandler(fileHandler)
log.addHandler(consoleHandler)

options = {
    "short": "hd:i:o:rfD",
    "long": [
        "help", "debug=", "infile=", "outfile=", "remove-background",
        "format-duration", "deduplicate"
    ],
    "descriptions": [
        "Print help message",
        "Set debug level",
        "Specify the input JSON",
        "Specify the output JSON, otherwise use stdout",
        "Remove background steps from output",
        "Format the duration",
        "Remove duplicate scenarios caused by @autoretry"
    ]
}


def convert(json_file, remove_background=False, duration_format=False, deduplicate=False):
    # json_nodes are the scopes available in behave/cucumber json: Feature -> elements(Scnerios) -> Steps
    json_nodes = ['feature', 'elements', 'steps']
    # These fields doesn't exist in cucumber report, there-fore when converting from behave, we need to delete these
    # fields.
    fields_not_exist_in_cucumber_json = ['status', 'step_type']

    def format_level(tree, index=0, id_counter=0):
        for item in tree:
            # Location in behave json translates to uri and line in cucumber json
            uri, line_number = item.pop("location").split(":")
            item["line"] = int(line_number)
            for field in fields_not_exist_in_cucumber_json:
                if field in item:
                    item.pop(field)
            if 'tags' in item:
                # Tags in behave are just a list of tag names, in cucumber every tag has a name and a line number.
                item['tags'] = [{"name": tag if tag.startswith('@') else '@' + tag, "line": item["line"] - 1} for tag in
                                item['tags']]
            if json_nodes[index] == 'steps':
                if 'result' in item:
                    # Because several problems with long error messages the message sub-stringed to maximum 2000 chars.
                    if 'error_message' in item["result"]:
                        error_msg = item["result"].pop('error_message')
                        item["result"]["error_message"] = str(
                            (str(error_msg).replace("\"", "").replace("\\'", ""))[:2000])
                    if 'duration' in item["result"] and duration_format:
                        item["result"]["duration"] = int(item["result"]["duration"] * 1000000000)
                else:
                    # In behave, skipped tests doesn't have result object in their json, there-fore when we generating
                    # Cucumber report for every skipped test we need to generated a new result with status skipped
                    item["result"] = {"status": "skipped", "duration": 0}
                if 'table' in item:
                    item['rows'] = []
                    t_line = 1
                    item['rows'].append({"cells": item['table']['headings'], "line": item["line"] + t_line})
                    for table_row in item['table']['rows']:
                        t_line += 1
                        item['rows'].append({"cells": table_row, "line": item["line"] + t_line})
            else:
                # uri is the name of the feature file the current item located
                item["uri"] = uri
                item["description"] = ""
                item["id"] = id_counter
                id_counter += 1
            # If the scope is not "steps" proceed with the recursion
            if index != 2 and json_nodes[index + 1] in item:
                item[json_nodes[index + 1]] = format_level(
                    item[json_nodes[index + 1]], index + 1, id_counter=id_counter
                )
        return tree

    # Option to remove background element because behave pushes it steps to all scenarios already
    if remove_background:
        for feature in json_file:
            if feature['elements'][0]['type'] == 'background':
                feature['elements'].pop(0)

    if deduplicate:
        def check_dupe(current_feature, current_scenario, previous_scenario):
            if "autoretry" not in current_feature['tags'] and "autoretry" not in current_scenario['tags']:
                return False
            if previous_scenario['keyword'] != current_scenario['keyword']:
                return False
            elif previous_scenario['location'] != current_scenario['location']:
                return False
            elif previous_scenario['name'] != current_scenario['name']:
                return False
            elif previous_scenario['tags'] != current_scenario['tags']:
                return False
            elif previous_scenario['type'] != current_scenario['type']:
                return False
            else:
                return True

        for feature in json_file:
            # Create a working list
            scenarios = []

            # For each scenario in the feature
            for scenario in feature['elements']:
                # Append the scenario to the working list
                scenarios.append(scenario)

                # Check the previous scenario
                try:
                    # See if the previous scenario exists and matches
                    previous_scenario = scenarios[-2]
                    if check_dupe(feature, scenario, previous_scenario):
                        # Remove the earlier scenario from the working list
                        scenarios.pop(-2)
                except IndexError:
                    # If we're at the beginning of the list, don't do anything
                    pass

            # Replace the existing list with the working list
            feature['elements'] = scenarios

    # Begin the recursion
    return format_level(json_file)


def usage():
    """Print out a usage message"""

    global options
    l = len(options['long'])
    options['shortlist'] = [s for s in options['short'] if s != ":"]

    print("python pytalos\integrations\cucumber.py")
    for i in range(l):
        print("    -{0}|--{1:20} {2}".format(options['shortlist'][i], options['long'][i], options['descriptions'][i]))


def main(argv):
    """Main"""
    global options

    opts = None
    try:
        opts, args = getopt.getopt(argv, options['short'], options['long'])
    except getopt.GetoptError:
        usage()
        exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            exit()
        elif opt in ("-d", "--debug"):
            try:
                arg = int(arg)
                log.debug("Debug level received: " + str(arg))
            except ValueError:
                log.warning("Invalid log level: " + arg)
                continue

            if 0 <= arg <= 5:
                log.setLevel(60 - (arg * 10))
                log.critical("Log level changed to: " + str(logging.getLevelName(60 - (arg * 10))))
            else:
                log.warning("Invalid log level: " + str(arg))

    infile = None
    outfile = None
    remove_background = False
    duration_format = False
    deduplicate = False

    for opt, arg in opts:
        if opt in ("-i", "--infile"):
            log.info("Input File: " + arg)
            infile = arg
        if opt in ("-o", "--outfile"):
            log.info("Output File: " + arg)
            outfile = arg
        if opt in ("-r", "--remove-background"):
            log.info("Remove Background: Enabled")
            remove_background = True
        if opt in ("-f", "--format-duration"):
            log.info("Format Duration: Enabled")
            duration_format = True
        if opt in ("-D", "--deduplicate"):
            log.info("Deduplicate: Enabled")
            deduplicate = True

    if infile is None:
        log.critical("No input JSON provided.")
        usage()
        exit(3)

    with open(infile) as f:
        cucumber_output = convert(json.load(f),
                                  remove_background=remove_background,
                                  duration_format=duration_format,
                                  deduplicate=deduplicate)

    if outfile is not None:
        with open(outfile, 'w') as f:
            json.dump(cucumber_output, f, indent=4, separators=(',', ': '))
    else:
        pprint(cucumber_output)


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        sys.exit(0)
    except EOFError:
        sys.exit(0)
    # except:
    #     sys.exit(0)
