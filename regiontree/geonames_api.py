import urllib.request
from time import sleep

import xmltodict

from regiontree.region import Region, Coordinate


class GeonamesAPI:
    def __init__(self, throttle: float, logging, user: str):
        self.base_url = 'http://api.geonames.org/'
        self.throttle = throttle
        self.logging = logging
        self.user = user

    def do_api_call(self, api: str, geoname_id: int) -> tuple:
        sleep(self.throttle)
        raw_dict = xmltodict.parse(urllib.request.urlopen(self.base_url + "%s?geonameId=%s&username=%s" % (api, geoname_id, self.user)).read())
        return self.log_status_message(raw_dict), raw_dict

    def children(self, geoname_id: int) -> set():
        result = set()
        failure, raw_result = self.do_api_call('children', geoname_id)

        if failure or raw_result['geonames']['totalResultsCount'] == '0':
            return result

        if raw_result['geonames']['totalResultsCount'] == '1':
            result.add(Region(int(raw_result['geonames']['geoname']['geonameId']),
                              raw_result['geonames']['geoname']['name'],
                              raw_result['geonames']['geoname']['toponymName'],
                              Coordinate(raw_result['geonames']['geoname']['lat'], raw_result['geonames']['geoname']['lng'])
                              ))
        else:
            for child in raw_result['geonames']['geoname']:
                result.add(Region(int(child['geonameId']), child['name'], child['toponymName'], Coordinate(child['lat'], child['lng'])))

        return result

    def name(self, geoname_id: int) -> dict:
        return self.do_api_call('get', geoname_id)[1]

    def log_status_message(self, raw_dict) -> bool:
        try:
            status_message = raw_dict['geonames']['status']['@message']
            if status_message.startswith('no children for'):
                self.logging.info(status_message)
                return True
            else:
                self.logging.warning(status_message)
                return True
        except KeyError:
            return False