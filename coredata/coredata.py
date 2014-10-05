""" Coredata REST api python library. """

import json
import requests

from enum import Enum
try:
    # Python3
    from urllib.parse import urlencode, urljoin, urlsplit, urlunsplit, parse_qs
except ImportError:
    # Python2
    from urllib import urlencode
    from urlparse import urljoin, urlsplit, urlunsplit, parse_qs


class CoredataError(Exception):

    """ A custom error that are thrown when Coredata makes a bobo. """

    pass


class Entity(Enum):

    """ A list of Coredata endpoints listed as a enumerate. """

    Docs = 'docs'
    Nav = 'nav'
    Comments = 'comments'
    Projects = 'projects'
    Contacts = 'contacts'
    Spaces = 'spaces'
    Dynatypes = 'dynatypes'
    Files = 'files'
    Tasks = 'tasks'
    User = 'user'
    Users = 'users'
    Valuelist = 'valuelists'
    Content = 'content'


class Utils:

    """
    Helper functions for Coredata.

    :todo: Remove this because of reasons.
    """

    @staticmethod
    def add_url_parameters(url, parameters):
        """ Add url parameters to URL. """
        scheme, netloc, path, query_string, fragment = urlsplit(url)
        query = parse_qs(query_string)
        query.update(parameters)
        return urlunsplit((scheme, netloc, path, urlencode(query), fragment))


class CoredataClient:

    """ A thin wrapper for requests to talk to the CoreData API. """

    def __init__(self, host, auth):
        """ Initialize the Coredata client. """
        # TODO: Parse the url rather than checking here.
        if 'http' not in host:
            raise ValueError('Missing scheme from host.')
        self.auth = auth
        self.host = urljoin(host, '/api/v2/')
        self.headers = {'content-type': 'application/json'}

    def edit(self, entity, id, payload, sync=True):
        """ Edit a document. """
        url = urljoin(self.host, entity.value + '/')
        url = urljoin(url, id + '/')
        params = {'sync': str(sync).lower()}
        url = Utils.add_url_parameters(url, params)
        r = requests.put(url, auth=self.auth, data=json.dumps(payload),
                         headers=self.headers)
        if r.status_code == 500:
            error_message = r.json()['error_message']
            raise CoredataError('Error! {error}'.format(error=error_message))

    def delete(self, entity, id, sync=True):
        """ Delete a document. """
        url = urljoin(self.host, entity.value + '/')
        url = urljoin(url, id + '/')
        params = {'sync': str(sync).lower()}
        url = Utils.add_url_parameters(url, params)
        r = requests.delete(url, auth=self.auth, headers=self.headers)
        if r.status_code == 500:
            error_message = r.json()['error_message']
            raise CoredataError('Error! {error}'.format(error=error_message))

    def create(self, entity, payload, sync=True):
        """ Create a new entity with the payload and return id of it. """
        url = urljoin(self.host, entity.value + '/')

        # Append the sync parameter to the URL
        params = {'sync': str(sync).lower()}
        url = Utils.add_url_parameters(url, params)

        # Make a post request with the payload to the appropriate entity
        # endpoint
        r = requests.post(url, auth=self.auth, data=json.dumps(payload),
                          headers=self.headers)

        if r.status_code == 500:
            error_message = r.json()['error_message']
            raise CoredataError('Error! {error}'.format(error=error_message))

        return r.headers['location'].rsplit('/', 1)[1]

    def get(self, entity, id=None, sub_entity=None, offset=0, limit=20,
            search_terms=None, sync=True):
        """
        Get all entities that fufill the given filtering if provided.

        :todo: Rename search_terms
        """
        url = urljoin(self.host, entity.value + '/')
        url = urljoin(url, id + '/') if id else url
        url = urljoin(url, sub_entity.value + '/') if sub_entity else url
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

            next_path = j['meta']['next']

            while next_path:
                offset += limit
                url = urljoin(self.host, entity.value + '/')
                url = urljoin(url, id + '/') if id else url
                url = urljoin(
                    url, sub_entity.value + '/') if sub_entity else url
                terms = {'offset': offset}
                url = Utils.add_url_parameters(
                    url, {'offset': offset})
                r = requests.get(url, auth=self.auth, headers=self.headers)
                j['objects'].extend(r.json()['objects'])
                next_path = r.json()['meta']['next']

            return j['objects']
        else:
            raise CoredataError(
                'Error occured! Status code is {code} for {url}'.format(
                    code=r.status_code, url=url))
