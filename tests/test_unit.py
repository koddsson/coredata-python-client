import json
import httpretty

from unittest import TestCase
from nose.tools import raises
from coredata import CoredataClient, Entity, CoredataError


@httpretty.activate
class TestAPI(TestCase):
    @raises(ValueError)
    def test_init(self):
        CoredataClient(
            host='derp://example.coredata.is', auth=('username', 'password'))


class TestEntity(TestCase):
    username = 'username'
    password = 'password'
    host = 'https://example.coredata.is'
    url = '{host}/api/v2/{entity}'

    def __init__(self, test_name):
        self.client = CoredataClient(
            host=self.host, auth=(self.username, self.password))
        super(TestEntity, self).__init__(test_name)

    def create_url(self, entity, id=None, sub_entity=None):
        url = self.url.format(host=self.host, entity=entity.value)
        if id:
            url += id + '/'
        if sub_entity:
            url += sub_entity.value
        return url


@httpretty.activate
class TestProjects(TestEntity):
    """
    Unit tests for /projects/ endpoint.
    """
    @raises(CoredataError)
    def test_get_project_error(self):
        httpretty.register_uri(
            httpretty.GET,
            self.create_url(Entity.Projects),
            status=500,
            body=json.dumps({'error_message': 'There was a error!'}),
            content_type="application/json; charset=utf-8")
        self.client.get(Entity.Projects, '')

    def test_get_a_single_project(self):
        project_id = 'f24203a0-3d8b-11e4-8e77-7ba23226dee9'
        httpretty.register_uri(
            httpretty.GET,
            self.create_url(Entity.Projects, project_id),
            body=open('tests/json/get_single_project.json').read(),
            content_type="application/json; charset=utf-8")
        projects = self.client.get(Entity.Projects, project_id)
        self.assertEqual(len(projects['objects']), 1)

    def test_getting_all_projects(self):
        httpretty.register_uri(
            httpretty.GET,
            self.create_url(Entity.Projects),
            responses=[
                httpretty.Response(
                    body=open('tests/json/get_projects.json').read()),
                httpretty.Response(
                    body=open('tests/json/get_projects_last.json').read()),
            ],
            content_type="application/json; charset=utf-8")
        r = self.client.get(Entity.Projects)
        self.assertEqual(len(r), 27)

    def test_getting_projects_with_filtering(self):
        httpretty.register_uri(
            httpretty.GET,
            self.create_url(Entity.Projects),
            body=open('tests/json/get_projects_filtered.json').read(),
            content_type="application/json; charset=utf-8")
        r = self.client.get(
            Entity.Projects, search_terms={'title__startswith': 'Y'})
        self.assertEqual(len(r), 1)

    def test_editing_a_project(self):
        project_id = 'f24203a0-3d8b-11e4-8e77-7ba23226dee9'
        httpretty.register_uri(
            httpretty.GET,
            self.create_url(Entity.Projects, project_id),
            responses=[
                httpretty.Response(
                    body=open('tests/json/get_single_project.json').read()),
                httpretty.Response(
                    body=open('tests/json/edit_project.json').read()),
            ],
            content_type="application/json; charset=utf-8")
        httpretty.register_uri(
            httpretty.PUT,
            self.create_url(Entity.Projects, project_id),
            status=204,
            content_type="application/json; charset=utf-8")
        projects = self.client.get(Entity.Projects, project_id)
        self.assertEqual(len(projects['objects']), 1)
        projects['objects'][0]['status_message'] = 'derp'
        self.client.edit(Entity.Projects, project_id, projects['objects'][0])
        edited_project = self.client.get(Entity.Projects, project_id)
        self.assertEqual(projects, edited_project)

    @raises(CoredataError)
    def test_editing_a_project_error(self):
        project_id = 'f24203a0-3d8b-11e4-8e77-7ba23226dee9'
        httpretty.register_uri(
            httpretty.GET,
            self.create_url(Entity.Projects, project_id),
            body=open('tests/json/get_single_project.json').read(),
            content_type="application/json; charset=utf-8")
        httpretty.register_uri(
            httpretty.PUT,
            self.create_url(Entity.Projects, project_id),
            status=500,
            body=json.dumps({'error_message': 'You can\'t do that'}),
            content_type="application/json; charset=utf-8")
        projects = self.client.get(Entity.Projects, project_id)
        self.assertEqual(len(projects['objects']), 1)
        projects['objects'][0]['status_message'] = 'derp'
        self.client.edit(Entity.Projects, project_id, projects['objects'][0])

    @raises(CoredataError)
    def test_deleting_a_project_error(self):
        project_id = 'f24203a0-3d8b-11e4-8e77-7ba23226dee9'
        httpretty.register_uri(
            httpretty.DELETE,
            self.create_url(Entity.Projects, project_id),
            status=500,
            body=json.dumps({'error_message': 'No way, Jose'}),
            content_type="application/json; charset=utf-8")
        self.client.delete(Entity.Projects, project_id)

    def test_deleting_a_project(self):
        project_id = 'f24203a0-3d8b-11e4-8e77-7ba23226dee9'
        httpretty.register_uri(
            httpretty.DELETE,
            self.create_url(Entity.Projects, project_id),
            content_type="application/json; charset=utf-8")
        self.client.delete(Entity.Projects, project_id)
        # TODO. Assert is deleted.

    @raises(CoredataError)
    def test_creating_a_project_error(self):
        # TODO: Assert error message
        project_url = ('http://example.coredata.is/doc/'
                       '9b4f8e70-45bd-11e4-a183-164230d1df67')
        httpretty.register_uri(
            httpretty.POST,
            self.create_url(Entity.Projects),
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

        r = self.client.create(Entity.Projects, payload)
        # TODO: I don't ever get here, do I?
        self.assertEqual(r['id'], 'f24203a0-3d8b-11e4-8e77-7ba23226dee9')

    def test_creating_a_project(self):
        project_id = '9b4f8e70-45bd-11e4-a183-164230d1df67'
        project_url = 'http://example.coredata.is/doc/{id}'.format(
            id=project_id)
        httpretty.register_uri(
            httpretty.POST,
            self.create_url(Entity.Projects),
            status=201,
            location=project_url,
            content_type="application/json; charset=utf-8")
        payload = {
            "space": "e634f784-3d8b-11e4-82a5-c3059141127e",
            "title": "Super important thing"
        }

        id = self.client.create(Entity.Projects, payload)
        self.assertEqual(id, project_id)


@httpretty.activate
class TestFiles(TestEntity):
    """
    Unit tests for /files/ endpoint.
    """
    def test_getting_content(self):
        file_id = '4ab3bb32-3e72-11e4-bfaa-ebeae41148db'
        # TODO: There is a better way to do this.
        try:
            # Python 3
            returned_content = open(
                'tests/files/get_file', encoding='latin-1').read()
        except TypeError:
            # Python 2
            returned_content = open('tests/files/get_file').read()
        httpretty.register_uri(
            httpretty.GET,
            self.create_url(Entity.Files, file_id, Entity.Content),
            body=returned_content
        )

        content = self.client.get(Entity.Files, file_id, Entity.Content)
        self.assertEqual(content, returned_content)

    @raises(CoredataError)
    def test_get_file_error(self):
        # TODO: Assert error message
        httpretty.register_uri(
            httpretty.GET,
            self.create_url(Entity.Files),
            status=500,
            body=json.dumps({'error_message': 'There was a error!'}),
            content_type="application/json; charset=utf-8")
        self.client.get(Entity.Files, '')

    def test_get_a_single_file(self):
        file_id = 'TODO: GET A RANDOM UUID'
        httpretty.register_uri(
            httpretty.GET,
            self.create_url(Entity.Files, file_id),
            body=open('tests/json/get_single_file.json').read(),
            content_type="application/json; charset=utf-8")
        projects = self.client.get(Entity.Files, file_id)
        self.assertEqual(len(projects['objects']), 1)

    def test_getting_all_files(self):
        httpretty.register_uri(
            httpretty.GET,
            self.create_url(Entity.Files),
            responses=[
                httpretty.Response(
                    body=open('tests/json/get_files.json').read()),
                httpretty.Response(
                    body=open('tests/json/get_files_last.json').read()),
            ],
            content_type="application/json; charset=utf-8")
        r = self.client.get(Entity.Files)
        self.assertEqual(len(r), 24)

    def test_getting_files_with_filtering(self):
        httpretty.register_uri(
            httpretty.GET,
            self.create_url(Entity.Files),
            body=open('tests/json/get_files.json').read(),
            content_type="application/json; charset=utf-8")
        r = self.client.get(
            Entity.Files, search_terms={'title__startswith': 'Y'})
        self.assertEqual(len(r), 1)

    def test_editing_a_file(self):
        file_id = 'f24203a0-3d8b-11e4-8e77-7ba23226dee9'
        httpretty.register_uri(
            httpretty.GET,
            self.create_url(Entity.Files, file_id),
            responses=[
                httpretty.Response(
                    body=open('tests/json/get_single_file.json').read()),
                httpretty.Response(
                    body=open('tests/json/edit_file.json').read())
            ],
            content_type="application/json; charset=utf-8")
        httpretty.register_uri(
            httpretty.PUT,
            self.create_url(Entity.Files, file_id),
            status=204,
            content_type="application/json; charset=utf-8")
        files = self.client.get(Entity.Files, file_id)
        self.assertEqual(len(files['objects']), 1)
        files['objects'][0]['status_message'] = 'derp'
        self.client.edit(Entity.Files, file_id, files['objects'][0])
        edited_file = self.client.get(Entity.Files, file_id)
        self.assertEqual(files, edited_file)

    @raises(CoredataError)
    def test_editing_a_file_error(self):
        # TODO: Assert error message
        file_id = 'f24203a0-3d8b-11e4-8e77-7ba23226dee9'
        httpretty.register_uri(
            httpretty.GET,
            self.create_url(Entity.Files, file_id),
            body=open('tests/json/get_single_file.json').read(),
            content_type="application/json; charset=utf-8")
        httpretty.register_uri(
            httpretty.PUT,
            self.create_url(Entity.Files, file_id),
            status=500,
            body=json.dumps({'error_message': 'You can\'t do that'}),
            content_type="application/json; charset=utf-8")
        files = self.client.get(Entity.Files, file_id)
        self.assertEqual(len(files['objects']), 1)
        files['objects'][0]['status_message'] = 'derp'
        self.client.edit(Entity.Files, file_id, files['objects'][0])

    @raises(CoredataError)
    def test_deleting_a_file_error(self):
        # TODO: Assert error message
        file_id = 'f24203a0-3d8b-11e4-8e77-7ba23226dee9'
        httpretty.register_uri(
            httpretty.DELETE,
            self.create_url(Entity.Files, file_id),
            status=500,
            body=json.dumps({'error_message': 'No way, Jose'}),
            content_type="application/json; charset=utf-8")
        self.client.delete(Entity.Files, file_id)

    def test_deleting_a_file(self):
        file_id = 'f24203a0-3d8b-11e4-8e77-7ba23226dee9'
        httpretty.register_uri(
            httpretty.DELETE,
            self.create_url(Entity.Files, file_id),
            content_type="application/json; charset=utf-8")
        self.client.delete(Entity.Files, file_id)
        # TODO. Assert is deleted.

    @raises(CoredataError)
    def test_creating_a_file_error(self):
        file_id = 'f24203a0-3d8b-11e4-8e77-7ba23226dee9'
        file_url = 'http://example.coredata.is/doc/{id}'.format(id=file_id)
        httpretty.register_uri(
            httpretty.POST,
            self.create_url(Entity.Files),
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

        r = self.client.create(Entity.Files, payload)
        # TODO: I don't ever get here, do I?
        self.assertEqual(r['id'], 'f24203a0-3d8b-11e4-8e77-7ba23226dee9')

    def test_creating_a_file(self):
        file_id = 'f24203a0-3d8b-11e4-8e77-7ba23226dee9'
        file_url = 'http://example.coredata.is/doc/{id}'.format(
            id=file_id)
        httpretty.register_uri(
            httpretty.POST,
            self.create_url(Entity.Files),
            status=201,
            location=file_url,
            content_type="application/json; charset=utf-8")
        payload = {
            "space": "TODO: Get a UUID here",
            "title": "Dis is a file created from the API"
        }

        id = self.client.create(Entity.Files, payload)
        self.assertEqual(id, file_id)
