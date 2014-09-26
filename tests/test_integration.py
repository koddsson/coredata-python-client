import httpretty

from unittest import TestCase
from CoredataAPI import CoredataClient, Entity


@httpretty.activate
class TestProjects(TestCase):
    def test_getting_all_projects(self):
        data = open('tests/json/get_projects2.json').read()
        httpretty.register_uri(httpretty.GET,
                               "https://example.coredata.is/api/v2/projects/",
                               body=data,
                               content_type="application/json; charset=utf-8")
        client = CoredataClient(host='https://example.coredata.is',
                                auth=('username', 'password'))
        r = client.get(Entity.Projects)
        self.assertEqual(len(r), 20)

    def test_creating_a_project(self):
        httpretty.register_uri(httpretty.POST,
                               "https://example.coredata.is/api/v2/projects/?sync=true",
                               status=201,
                               location='http://example.coredata.is/doc/9b4f8e70-45bd-11e4-a183-164230d1df67',
                               content_type="application/json; charset=utf-8")
        data = open('tests/json/get_single_project.json').read()
        httpretty.register_uri(httpretty.GET,
                               "http://example.coredata.is/doc/9b4f8e70-45bd-11e4-a183-164230d1df67",
                               body=data,
                               content_type="application/json; charset=utf-8")
        payload = {
            "space": "e634f784-3d8b-11e4-82a5-c3059141127e",
            "title": "Super important thing"
        }

        client = CoredataClient(host='https://example.coredata.is',
                                auth=('username', 'password'))
        r = client.create(Entity.Projects, payload)
        self.assertEqual(r['id'], 'f24203a0-3d8b-11e4-8e77-7ba23226dee9')
