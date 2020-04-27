import re

import requests


class ScrapeHelper:
    @staticmethod
    def get_code():
        url = 'https://www.mapdevelopers.com/js/geocode_service.js'
        res = requests.get(url)
        return parse_by_regex(res.text)
    @staticmethod
    def get_lcode_lid():
        url = 'https://www.mapdevelopers.com/geocode_tool.php'
        res = requests.get(url)
        lcode = parse_lcode_by_regex(res.text)
        lid = parse_lid_by_regex(res.text)
        return [lcode, lid]

def parse_by_regex(test_str):
    try:
        regex = r"(&code=)([a-z0-9]+)(\")"
        matches = re.finditer(regex, test_str, re.MULTILINE)
        for matchNum, match in enumerate(matches, start=1):
            code = match.group(2)
            return code
    except:
        print('error')

def parse_lcode_by_regex(test_str):
    try:
        regex = r"(lcode\ \=\ \")(.*)(\")"
        matches = re.finditer(regex, test_str, re.MULTILINE)
        for matchNum, match in enumerate(matches, start=1):
            lcode = match.group(2)
            print("LCODE :")
            print(lcode)
            return lcode
    except:
        print('error')

def parse_lid_by_regex(test_str):
    try:
        regex = r"(lid\ \=\ \")(.*)(\")"
        matches = re.finditer(regex, test_str, re.MULTILINE)
        for matchNum, match in enumerate(matches, start=1):
            lid = match.group(2)
            print("LID :")
            print(lid)
            return lid
    except:
        print('error')