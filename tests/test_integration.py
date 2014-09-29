import json
import httpretty

from unittest import TestCase
from nose.tools import raises
from coredata import CoredataClient, Entity, CoredataError


@httpretty.activate
class TestAPI(TestCase):
    @raises(ValueError)
    def test_init(self):
        CoredataClient(host='derp://example.coredata.is',
                       auth=('username', 'password'))


@httpretty.activate
class TestProjects(TestCase):
    @raises(CoredataError)
    def test_get_project_error(self):
        httpretty.register_uri(
            httpretty.GET,
            "https://example.coredata.is/api/v2/projects/",
            status=500,
            body=json.dumps({'error_message': 'There was a error!'}),
            content_type="application/json; charset=utf-8")
        client = CoredataClient(host='https://example.coredata.is',
                                auth=('username', 'password'))
        client.get(Entity.Projects, '')

    def test_get_a_single_project(self):
        httpretty.register_uri(
            httpretty.GET,
            ('https://example.coredata.is/api/v2/projects/'
             'f24203a0-3d8b-11e4-8e77-7ba23226dee9/?sync=true'),
            body=open('tests/json/get_single_project.json').read(),
            content_type="application/json; charset=utf-8")
        client = CoredataClient(host='https://example.coredata.is',
                                auth=('username', 'password'))
        projects = client.get(
            Entity.Projects, 'f24203a0-3d8b-11e4-8e77-7ba23226dee9')
        self.assertEqual(len(projects['objects']), 1)

    def test_getting_all_projects(self):
        httpretty.register_uri(
            httpretty.GET,
            "https://example.coredata.is/api/v2/projects/",
            responses=[
                httpretty.Response(
                    body=open('tests/json/get_projects.json').read()),
                httpretty.Response(
                    body=open('tests/json/get_projects_last.json').read()),
            ],
            content_type="application/json; charset=utf-8")
        client = CoredataClient(
            host='https://example.coredata.is',
            auth=('username', 'password'))
        r = client.get(Entity.Projects)
        self.assertEqual(len(r), 27)

    def test_getting_projects_with_filtering(self):
        httpretty.register_uri(
            httpretty.GET,
            "https://example.coredata.is/api/v2/projects/",
            body=open('tests/json/get_projects_filtered.json').read(),
            content_type="application/json; charset=utf-8")
        client = CoredataClient(
            host='https://example.coredata.is',
            auth=('username', 'password'))
        r = client.get(Entity.Projects,
                       search_terms={'title__startswith': 'Y'})
        self.assertEqual(len(r), 1)

    def test_editing_a_project(self):
        httpretty.register_uri(
            httpretty.GET,
            ('https://example.coredata.is/api/v2/projects/'
             'f24203a0-3d8b-11e4-8e77-7ba23226dee9/?sync=true'),
            responses=[
                httpretty.Response(
                    body=open('tests/json/get_single_project.json').read()),
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

    @raises(CoredataError)
    def test_editing_a_project_error(self):
        httpretty.register_uri(
            httpretty.GET,
            ('https://example.coredata.is/api/v2/projects/'
             'f24203a0-3d8b-11e4-8e77-7ba23226dee9/?sync=true'),
            body=open('tests/json/get_single_project.json').read(),
            content_type="application/json; charset=utf-8")
        httpretty.register_uri(
            httpretty.PUT,
            ('https://example.coredata.is/api/v2/projects/'
             'f24203a0-3d8b-11e4-8e77-7ba23226dee9?sync=true'),
            status=500,
            body=json.dumps({'error_message': 'You can\'t do that'}),
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

    @raises(CoredataError)
    def test_deleting_a_project_error(self):
        httpretty.register_uri(
            httpretty.DELETE,
            ('https://example.coredata.is/api/v2/projects/'
             'f24203a0-3d8b-11e4-8e77-7ba23226dee9?sync=true'),
            status=500,
            body=json.dumps({'error_message': 'No way, Jose'}),
            content_type="application/json; charset=utf-8")
        client = CoredataClient(host='https://example.coredata.is',
                                auth=('username', 'password'))
        client.delete(Entity.Projects, 'f24203a0-3d8b-11e4-8e77-7ba23226dee9')

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

    @raises(CoredataError)
    def test_creating_a_project_error(self):
        project_url = ('http://example.coredata.is/doc/'
                       '9b4f8e70-45bd-11e4-a183-164230d1df67')
        httpretty.register_uri(
            httpretty.POST,
            "https://example.coredata.is/api/v2/projects/?sync=true",
            status=500,
            body=json.dumps({'error_message': '#wontfix'}),
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

    def test_creating_a_project(self):
        project_id = '9b4f8e70-45bd-11e4-a183-164230d1df67'
        project_url = 'http://example.coredata.is/doc/{id}'.format(
            id=project_id)
        httpretty.register_uri(
            httpretty.POST,
            "https://example.coredata.is/api/v2/projects/?sync=true",
            status=201,
            location=project_url,
            content_type="application/json; charset=utf-8")
        payload = {
            "space": "e634f784-3d8b-11e4-82a5-c3059141127e",
            "title": "Super important thing"
        }

        client = CoredataClient(host='https://example.coredata.is',
                                auth=('username', 'password'))
        id = client.create(Entity.Projects, payload)
        self.assertEqual(id, project_id)
