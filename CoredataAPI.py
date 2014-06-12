"""
Coredata API Python Client

Usage:
  coredata_api.py create <entity> <file> --host=<host> --auth=<auth> [--sync]
  coredata_api.py get <entity> --host=<host> --auth=<auth> [--sync]
  coredata_api.py -h | --help
  coredata_api.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  --sync        Make requests syncronus (default is async)
"""
from docopt import docopt

import json
import requests

from enum import Enum
from pprint import pprint
from urllib import urlencode
from urlparse import urljoin, urlsplit, urlunsplit, parse_qs


class Entity(Enum):
    Projects = 'projects/'
    Contacts = 'contacts/'
    Spaces = 'spaces/'
    Dynatypes = 'dynatypes/'
    Files = 'files/'
    Tasks = 'tasks/'
    User = 'user/'
    Users = 'users/'
    Valuelist = 'valuelists/'


class CoredataClient:
    """
    A thin wrapper for requests to talk to the CoreData API.
    """
    def __init__(self, host, auth):
        self.auth = auth
        self.host = urljoin(host, '/api/v2/')
        self.headers = {'content-type': 'application/json'}

    def _add_url_parameters(self, url, parameters):
        scheme, netloc, path, query_string, fragment = urlsplit(url)
        query = parse_qs(query_string)
        query.update(parameters)
        return urlunsplit((scheme, netloc, path, urlencode(query), fragment))

    def create(self, entity, payload, sync=True, fetch_entity=True):
        """
        Creates a new entity with the payload and returns the id of that
        new entity in the API.
        """
        url = urljoin(self.host, entity.value)

        # Append the sync parameter to the URL
        params = {'sync': str(sync).lower()}
        url = self._add_url_parameters(url, params)

        # Make a post request with the payload to the appropriate entity
        # endpoint
        r = requests.post(url, auth=self.auth, data=json.dumps(payload),
                          headers=self.headers)

        if r.status_code == 500:
            error_message = r.json()['error_message']
            raise Exception('Error! {error}'.format(error=error_message))

        # Fetch the location header from the response that contains the
        # endpoint for the newly created entity.
        url = r.headers['location']
        if sync and fetch_entity:
            # We get the entity from location if requested and return it
            return requests.get(
                url, auth=self.auth, headers=self.headers).json()
        else:
            # Otherwise just return the location of the element.
            return url

    def get(self, entity, id=None, limit=20):
        """
        Gets either all the entities or a specific one if id is supplied
        """
        url = urljoin(self.host, entity.value)
        url = urljoin(url, id) if id else url
        url = self._add_url_parameters(url, {'limit': limit}) if limit else url
        return requests.get(url, auth=self.auth, headers=self.headers).json()


if __name__ == '__main__':
    arguments = docopt(__doc__, version='Naval Fate 2.0')
    host = arguments['--host']
    auth = tuple(arguments['--auth'].split(':'))
    client = CoredataClient(host, auth)
    entity = Entity(arguments['<entity>'].lower() + '/')
    if arguments['get']:
        pprint(client.get(entity))
    elif arguments['create']:
        payload = json.loads(open(arguments['<file>']).read())
        pprint(client.create(entity, payload, arguments['--sync']))
