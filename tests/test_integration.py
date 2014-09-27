import json
import httpretty

from unittest import TestCase
from nose.tools import raises
from CoredataAPI import CoredataClient, Entity, CoredataError


@httpretty.activate
class TestAPI(TestCase):
    @raises(ValueError)
    def test_init(self):
        CoredataClient(host='derp://example.coredata.is',
                       auth=('username', 'password'))

    @raises(CoredataError)
    def test_error_handling(self):
        httpretty.register_uri(
            httpretty.GET,
            "https://example.coredata.is/api/v2/projects/",
            status=500,
            body=json.dumps({'error_message': 'There was a error!'}),
            content_type="application/json; charset=utf-8")
        client = CoredataClient(host='https://example.coredata.is',
                                auth=('username', 'password'))
        r = client.get(Entity.Projects, '')
        print r


@httpretty.activate
class TestProjects(TestCase):
    def test_editing_a_project(self):
        httpretty.register_uri(
            httpretty.GET,
            ('https://example.coredata.is/api/v2/projects/'
             'f24203a0-3d8b-11e4-8e77-7ba23226dee9/?sync=true'),
            responses=[
                httpretty.Response(
                    body=open('tests/json/get_project.json').read()),
                httpretty.Response(
                    body=open('tests/json/edit_project.json').read()),
            ],
            content_type="application/json; charset=utf-8")
        httpretty.register_uri(
            httpretty.PUT,
            ('https://example.coredata.is/api/v2/projects/'
             'f24203a0-3d8b-11e4-8e77-7ba23226dee9?sync=true'),
            status=204,
            content_type="application/json; charset=utf-8")
        client = CoredataClient(host='https://example.coredata.is',
                                auth=('username', 'password'))
        projects = client.get(
            Entity.Projects, 'f24203a0-3d8b-11e4-8e77-7ba23226dee9')
        self.assertEqual(len(projects['objects']), 1)
        projects['objects'][0]['status_message'] = 'derp'
        client.edit(
            Entity.Projects, 'f24203a0-3d8b-11e4-8e77-7ba23226dee9',
            projects['objects'][0])
        edited_project = client.get(
            Entity.Projects, 'f24203a0-3d8b-11e4-8e77-7ba23226dee9')
        self.assertEqual(projects, edited_project)

    def test_deleting_a_project(self):
        httpretty.register_uri(
            httpretty.DELETE,
            ('https://example.coredata.is/api/v2/projects/'
             'f24203a0-3d8b-11e4-8e77-7ba23226dee9?sync=true'),
            content_type="application/json; charset=utf-8")
        client = CoredataClient(host='https://example.coredata.is',
                                auth=('username', 'password'))
        client.delete(Entity.Projects, 'f24203a0-3d8b-11e4-8e77-7ba23226dee9')
        # TODO. Assert is deleted.

    def test_getting_all_projects(self):
        data = open('tests/json/get_projects.json').read()
        httpretty.register_uri(httpretty.GET,
                               "https://example.coredata.is/api/v2/projects/",
                               body=data,
                               content_type="application/json; charset=utf-8")
        client = CoredataClient(host='https://example.coredata.is',
                                auth=('username', 'password'))
        r = client.get(Entity.Projects)
        self.assertEqual(len(r), 20)

    def test_creating_a_project(self):
        project_url = ('http://example.coredata.is/doc/'
                       '9b4f8e70-45bd-11e4-a183-164230d1df67')
        httpretty.register_uri(
            httpretty.POST,
            "https://example.coredata.is/api/v2/projects/?sync=true",
            status=201,
            location=project_url,
            content_type="application/json; charset=utf-8")
        data = open('tests/json/get_single_project.json').read()
        httpretty.register_uri(
            httpretty.GET,
            project_url,
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
