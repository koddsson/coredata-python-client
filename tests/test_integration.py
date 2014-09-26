import httpretty

import codecs
from unittest import TestCase
from CoredataAPI import CoredataClient, Entity

@httpretty.activate
class TestProjects(TestCase):
    def test_getting_all_projects(self):
        httpretty.register_uri(httpretty.GET, "https://example.coredata.is/api/v2/projects/",
                               body=open('tests/json/get_projects2.json').read(),
                               content_type="application/json; charset=utf-8")
        client = CoredataClient(host='https://example.coredata.is',
                                auth=('username', 'password'))
        r = client.get(Entity.Projects)
        self.assertEqual(len(r), 20)
