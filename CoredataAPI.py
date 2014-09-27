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
try:
    # Python3
    from urllib.parse import urlencode, urljoin, urlsplit, urlunsplit, parse_qs
except ImportError:
    # Python2
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
    Content = 'content/'


class Utils:
    @staticmethod
    def add_url_parameters(url, parameters):
        scheme, netloc, path, query_string, fragment = urlsplit(url)
        query = parse_qs(query_string)
        query.update(parameters)
        return urlunsplit((scheme, netloc, path, urlencode(query), fragment))


class CoredataClient:
    """
    A thin wrapper for requests to talk to the CoreData API.
    """
    def __init__(self, host, auth):
        if 'http' not in host:
            raise ValueError('Missing scheme from host.')
        self.auth = auth
        self.host = urljoin(host, '/api/v2/')
        self.headers = {'content-type': 'application/json'}

    def edit(self, entity, id, payload, sync=True):
        """
        Edits a document
        """
        url = urljoin(self.host, entity.value)
        url = urljoin(url, id)
        params = {'sync': str(sync).lower()}
        url = Utils.add_url_parameters(url, params)
        r = requests.put(url, auth=self.auth, data=json.dumps(payload),
                         headers=self.headers)
        if r.status_code == 500:
            error_message = r.json()['error_message']
            raise Exception('Error! {error}'.format(error=error_message))

    def delete(self, entity, id, sync=True):
        """
        Deletes a document
        """
        url = urljoin(self.host, entity.value)
        url = urljoin(url, id)
        params = {'sync': str(sync).lower()}
        url = Utils.add_url_parameters(url, params)
        r = requests.delete(url, auth=self.auth, headers=self.headers)
        if r.status_code == 500:
            error_message = r.json()['error_message']
            raise Exception('Error! {error}'.format(error=error_message))

    def create(self, entity, payload, sync=True, fetch_entity=True):
        """
        Creates a new entity with the payload and returns the id of that
        new entity in the API.
        """
        url = urljoin(self.host, entity.value)

        # Append the sync parameter to the URL
        params = {'sync': str(sync).lower()}
        url = Utils.add_url_parameters(url, params)

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

    def get(self, entity, id=None, sub_entity=None, offset=0, limit=20,
            search_terms=None, sync=True):
        """
        Gets all entities that fufill the given filtering if provided.
        """
        url = urljoin(self.host, entity.value)
        url = urljoin(url, id + '/') if id else url
        url = urljoin(url, sub_entity.value) if sub_entity else url
        terms = {'sync': str(sync).lower()}
        if search_terms:
            terms.update(search_terms)
        if not id:
            terms.update({'limit': limit, 'offset': offset})
        url = Utils.add_url_parameters(url, terms)
        r = requests.get(url, auth=self.auth, headers=self.headers)
        if sub_entity == Entity.Content:
            return r.content
        elif r.ok:
            j = r.json()

            if 'meta' not in j:
                # TODO: Fix error in API. No meta data returned when getting a
                # single object.
                return {'objects': [j]}

            if limit:
                return j['objects']

            next_path = j['meta']['next']

            while next_path:
                offset += limit
                url = urljoin(self.host, entity.value)
                url = urljoin(url, id + '/') if id else url
                url = urljoin(url, sub_entity.value) if sub_entity else url
                terms = {'offset': offset}
                url = Utils.add_url_parameters(
                    url, {'offset': offset})
                r = requests.get(url, auth=self.auth, headers=self.headers)
                j['objects'].extend(r.json()['objects'])
                next_path = r.json()['meta']['next']

            return j['objects']
        else:
            raise Exception(
                'Error occured! Status code is {code} for {url}'.format(
                    code=r.status_code, url=url))

if __name__ == '__main__':
    arguments = docopt(__doc__, version='Coredata Python Client 0.1')
    host = arguments['--host']
    auth = tuple(arguments['--auth'].split(':'))
    client = CoredataClient(host, auth)
    entity = Entity(arguments['<entity>'].lower() + '/')
    if arguments['get']:
        pprint(client.get(entity))
    elif arguments['create']:
        payload = json.loads(open(arguments['<file>']).read())
        pprint(client.create(entity, payload, arguments['--sync']))
