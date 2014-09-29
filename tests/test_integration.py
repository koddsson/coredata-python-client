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
        # TODO: Assert error message
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
        # TODO: I don't ever get here, do I?
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


@httpretty.activate
class TestFiles(TestCase):
    def test_getting_content(self):
        file_id = '4ab3bb32-3e72-11e4-bfaa-ebeae41148db'
        file_url = ('https://example.coredata.is'
                    '/api/v2/files/{id}/content/?sync=true'.format(
                        id=file_id))
        # TODO: There is a better way to do this.
        try:
            # Python 3
            returned_content = open(
                'tests/files/get_file', encoding='latin-1').read()
        except TypeError:
            # Python 2
            returned_content = open('tests/files/get_file').read()
        httpretty.register_uri(
            httpretty.GET, file_url, body=returned_content
        )

        client = CoredataClient(host='https://example.coredata.is',
                                auth=('username', 'password'))
        content = client.get(Entity.Files, file_id, Entity.Content)
        self.assertEqual(content, returned_content)

    @raises(CoredataError)
    def test_get_file_error(self):
        # TODO: Assert error message
        httpretty.register_uri(
            httpretty.GET,
            "https://example.coredata.is/api/v2/files/",
            status=500,
            body=json.dumps({'error_message': 'There was a error!'}),
            content_type="application/json; charset=utf-8")
        client = CoredataClient(host='https://example.coredata.is',
                                auth=('username', 'password'))
        client.get(Entity.Files, '')

    def test_get_a_single_file(self):
        file_id = 'TODO: GET A RANDOM UUID'
        httpretty.register_uri(
            httpretty.GET,
            'https://example.coredata.is/api/v2/files/{id}/?sync=true'.format(
                id=file_id),
            body=open('tests/json/get_single_file.json').read(),
            content_type="application/json; charset=utf-8")
        client = CoredataClient(host='https://example.coredata.is',
                                auth=('username', 'password'))
        projects = client.get(
            Entity.Files, file_id)
        self.assertEqual(len(projects['objects']), 1)

    def test_getting_all_files(self):
        httpretty.register_uri(
            httpretty.GET,
            "https://example.coredata.is/api/v2/files/",
            responses=[
                httpretty.Response(
                    body=open('tests/json/get_files.json').read()),
                httpretty.Response(
                    body=open('tests/json/get_files_last.json').read()),
            ],
            content_type="application/json; charset=utf-8")
        client = CoredataClient(
            host='https://example.coredata.is',
            auth=('username', 'password'))
        r = client.get(Entity.Files)
        self.assertEqual(len(r), 24)

    def test_getting_files_with_filtering(self):
        httpretty.register_uri(
            httpretty.GET,
            "https://example.coredata.is/api/v2/files/",
            body=open('tests/json/get_files.json').read(),
            content_type="application/json; charset=utf-8")
        client = CoredataClient(
            host='https://example.coredata.is',
            auth=('username', 'password'))
        r = client.get(
            Entity.Files, search_terms={'title__startswith': 'Y'})
        self.assertEqual(len(r), 1)

    def test_editing_a_file(self):
        file_id = 'f24203a0-3d8b-11e4-8e77-7ba23226dee9'
        httpretty.register_uri(
            httpretty.GET,
            'https://example.coredata.is/api/v2/files/{id}/?sync=true'.format(
                id=file_id),
            responses=[
                httpretty.Response(
                    body=open('tests/json/get_single_file.json').read()),
                httpretty.Response(
                    body=open('tests/json/edit_file.json').read())
            ],
            content_type="application/json; charset=utf-8")
        httpretty.register_uri(
            httpretty.PUT,
            'https://example.coredata.is/api/v2/files/{id}?sync=true'.format(
                id=file_id),
            status=204,
            content_type="application/json; charset=utf-8")
        client = CoredataClient(
            host='https://example.coredata.is', auth=('username', 'password'))
        files = client.get(Entity.Files, file_id)
        self.assertEqual(len(files['objects']), 1)
        files['objects'][0]['status_message'] = 'derp'
        client.edit(
            Entity.Files, file_id, files['objects'][0])
        edited_file = client.get(Entity.Files, file_id)
        self.assertEqual(files, edited_file)

    @raises(CoredataError)
    def test_editing_a_file_error(self):
        # TODO: Assert error message
        file_id = 'f24203a0-3d8b-11e4-8e77-7ba23226dee9'
        httpretty.register_uri(
            httpretty.GET,
            'https://example.coredata.is/api/v2/files/{id}/?sync=true'.format(
                id=file_id),
            body=open('tests/json/get_single_file.json').read(),
            content_type="application/json; charset=utf-8")
        httpretty.register_uri(
            httpretty.PUT,
            'https://example.coredata.is/api/v2/files/{id}?sync=true'.format(
                id=file_id),
            status=500,
            body=json.dumps({'error_message': 'You can\'t do that'}),
            content_type="application/json; charset=utf-8")
        client = CoredataClient(
            host='https://example.coredata.is', auth=('username', 'password'))
        files = client.get(Entity.Files, file_id)
        self.assertEqual(len(files['objects']), 1)
        files['objects'][0]['status_message'] = 'derp'
        client.edit(Entity.Files, file_id, files['objects'][0])

    @raises(CoredataError)
    def test_deleting_a_file_error(self):
        # TODO: Assert error message
        file_id = 'f24203a0-3d8b-11e4-8e77-7ba23226dee9'
        httpretty.register_uri(
            httpretty.DELETE,
            'https://example.coredata.is/api/v2/files/{id}?sync=true'.format(
                id=file_id),
            status=500,
            body=json.dumps({'error_message': 'No way, Jose'}),
            content_type="application/json; charset=utf-8")
        client = CoredataClient(
            host='https://example.coredata.is', auth=('username', 'password'))
        client.delete(Entity.Files, file_id)

    def test_deleting_a_file(self):
        file_id = 'f24203a0-3d8b-11e4-8e77-7ba23226dee9'
        httpretty.register_uri(
            httpretty.DELETE,
            'https://example.coredata.is/api/v2/files/{id}?sync=true'.format(
                id=file_id),
            content_type="application/json; charset=utf-8")
        client = CoredataClient(
            host='https://example.coredata.is', auth=('username', 'password'))
        client.delete(Entity.Files, file_id)
        # TODO. Assert is deleted.

    @raises(CoredataError)
    def test_creating_a_file_error(self):
        file_id = 'f24203a0-3d8b-11e4-8e77-7ba23226dee9'
        file_url = 'http://example.coredata.is/doc/{id}'.format(id=file_id)
        httpretty.register_uri(
            httpretty.POST,
            "https://example.coredata.is/api/v2/files/?sync=true",
            status=500,
            body=json.dumps({'error_message': '#wontfix'}),
            location=file_url,
            content_type="application/json; charset=utf-8")
        data = open('tests/json/get_single_file.json').read()
        httpretty.register_uri(
            httpretty.GET, file_url, body=data,
            content_type="application/json; charset=utf-8")
        # TODO: Make sure that this is the right payload.
        payload = {
            "space": "PUT A UUID here",
            "title": "Dis is a file title"
        }

        client = CoredataClient(
            host='https://example.coredata.is', auth=('username', 'password'))
        r = client.create(Entity.Files, payload)
        # TODO: I don't ever get here, do I?
        self.assertEqual(r['id'], 'f24203a0-3d8b-11e4-8e77-7ba23226dee9')

    def test_creating_a_file(self):
        file_id = 'f24203a0-3d8b-11e4-8e77-7ba23226dee9'
        file_url = 'http://example.coredata.is/doc/{id}'.format(
            id=file_id)
        httpretty.register_uri(
            httpretty.POST,
            "https://example.coredata.is/api/v2/files/?sync=true",
            status=201,
            location=file_url,
            content_type="application/json; charset=utf-8")
        payload = {
            "space": "TODO: Get a UUID here",
            "title": "Dis is a file created from the API"
        }

        client = CoredataClient(
            host='https://example.coredata.is', auth=('username', 'password'))
        id = client.create(Entity.Files, payload)
        self.assertEqual(id, file_id)
