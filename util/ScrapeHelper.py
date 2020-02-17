import re

import requests


class ScrapeHelper:
    @staticmethod
    def get_code():
        url = 'https://www.mapdevelopers.com/js/geocode_service.js'
        res = requests.get(url)
        return parse_by_regex(res.text)


def parse_by_regex(test_str):
    try:
        regex = r"(&code=)([a-z0-9]+)(\")"
        matches = re.finditer(regex, test_str, re.MULTILINE)
        for matchNum, match in enumerate(matches, start=1):
            code = match.group(2)
            return code
    except:
        print('error')
