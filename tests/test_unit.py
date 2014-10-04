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


class EntityTestCase(object):

    """
    Helper functions for testing the Coredata API.

    :todo:
        - When functions here start with the `test_` prefix they are
        automatically called for each class that subclasses this one. Maybe we
        can dynamically run the standard tests for them.
        - Add tests for DELETE.
        - Add tests for PUT.
    """

    username = 'username'
    password = 'password'
    host = 'https://example.coredata.is'
    url = '{host}/api/v2/{entity}'

    def create_url(self, entity, id=None, sub_entity=None):
        url = self.url.format(host=self.host, entity=entity.value + '/')
        if id:
            url += id + '/'
        if sub_entity:
            url += sub_entity.value + '/'
        return url

    def test_create_a_entity(self):
        url = 'http://example.coredata.is/doc/{id}'.format(
            id=self.entity_id)
        httpretty.register_uri(
            httpretty.POST,
            self.create_url(self.entity),
            status=201,
            location=url,
            content_type="application/json; charset=utf-8")

        # TODO: Is the payload always the same?
        payload = {
            "space": "TODO: Get a UUID here",
            "title": "Dis is a comment created from the API"
        }

        id = self.client.create(self.entity, payload)
        self.assertEqual(id, self.entity_id)

    @raises(CoredataError)
    def test_create_a_entity_error(self):
        url = 'http://example.coredata.is/doc/{id}'.format(id=self.entity_id)
        httpretty.register_uri(
            httpretty.POST,
            self.create_url(self.entity),
            status=500,
            body=json.dumps({'error_message': '#wontfix'}),
            location=url,
            content_type="application/json; charset=utf-8")
        data = open('tests/json/get_single_{entity}.json'.format(
            entity=self.entity.value)).read()
        httpretty.register_uri(
            httpretty.GET, url, body=data,
            content_type="application/json; charset=utf-8")
        # TODO: Make sure that this is the right payload.
        payload = {
            "doc_id": "PUT A UUID here",
            "text": "Dis is a contact title"
        }

        r = self.client.create(self.entity, payload)
        # TODO: I don't ever get here, do I?
        self.assertEqual(r['id'], self.entity_id)

    def test_get_a_single_entity(self):
        httpretty.register_uri(
            httpretty.GET,
            self.create_url(self.entity, self.entity_id),
            body=open('tests/json/get_single_{entity}.json'.format(
                entity=self.entity.value)).read(),
            content_type="application/json; charset=utf-8")
        entities = self.client.get(self.entity, self.entity_id)
        self.assertEqual(len(entities['objects']), 1)

    @raises(CoredataError)
    def test_getting_a_single_entity_error(self):
        # TODO: Assert error message
        httpretty.register_uri(
            httpretty.GET,
            self.create_url(self.entity),
            status=500,
            body=json.dumps({'error_message': 'There was a error!'}),
            content_type="application/json; charset=utf-8")
        self.client.get(self.entity, '')

    def test_getting_all_entities(self):
        httpretty.register_uri(
            httpretty.GET,
            self.create_url(self.entity),
            body=open('tests/json/get_all_{entity}.json'.format(
                entity=self.entity.value)).read(),
            content_type="application/json; charset=utf-8")
        r = self.client.get(self.entity)
        self.assertEqual(len(r), self.entity_count)

    @raises(CoredataError)
    def test_getting_all_entities_error(self):
        # TODO: Assert error message
        httpretty.register_uri(
            httpretty.GET,
            self.create_url(self.entity),
            status=500,
            body=json.dumps({'error_message': 'There was a error!'}),
            content_type="application/json; charset=utf-8")
        self.client.get(self.entity, '')


@httpretty.activate
class TestProjects(TestCase, EntityTestCase):
    """
    Unit tests for /projects/ endpoint.
    """
    entity = Entity.Projects
    entity_id = 'f24203a0-3d8b-11e4-8e77-7ba23226dee9'
    entity_count = 20

    def setUp(self):
        self.client = CoredataClient(
            host=self.host, auth=(self.username, self.password))

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
                    body=open('tests/json/get_single_projects.json').read()),
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
            body=open('tests/json/get_single_projects.json').read(),
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


@httpretty.activate
class TestFiles(TestCase, EntityTestCase):
    entity = Entity.Files
    entity_id = '4ab3bb32-3e72-11e4-bfaa-ebeae41148db'
    entity_count = 4

    def setUp(self):
        self.client = CoredataClient(
            host=self.host, auth=(self.username, self.password))

    def test_getting_content(self):
        file_id = '4ab3bb32-3e72-11e4-bfaa-ebeae41148db'
        # TODO: There is a better way to do this.
        returned_content = open('tests/files/get_file', 'rb').read()
        httpretty.register_uri(
            httpretty.GET,
            self.create_url(Entity.Files, file_id, Entity.Content),
            body=returned_content
        )

        content = self.client.get(Entity.Files, file_id, Entity.Content)
        self.assertEqual(content, returned_content)

    def test_getting_files_with_filtering(self):
        httpretty.register_uri(
            httpretty.GET,
            self.create_url(Entity.Files),
            body=open('tests/json/get_files_filtering.json').read(),
            content_type="application/json; charset=utf-8")
        r = self.client.get(
            Entity.Files, search_terms={'title__startswith': 'Y'})
        self.assertEqual(len(r), 6)

    def test_editing_a_file(self):
        file_id = 'f24203a0-3d8b-11e4-8e77-7ba23226dee9'
        httpretty.register_uri(
            httpretty.GET,
            self.create_url(Entity.Files, file_id),
            responses=[
                httpretty.Response(
                    body=open('tests/json/get_single_files.json').read()),
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
        files['objects'][0]['title'] = 'All your base are belong to us'
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
            body=open('tests/json/get_single_files.json').read(),
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


@httpretty.activate
class TestComments(TestCase, EntityTestCase):
    entity = Entity.Comments
    entity_id = 'f24203a0-3d8b-11e4-8e77-7ba23226dee9'
    entity_count = 1

    def setUp(self):
        self.client = CoredataClient(
            host=self.host, auth=(self.username, self.password))


@httpretty.activate
class TestContacts(TestCase, EntityTestCase):
    entity = Entity.Contacts
    entity_id = 'f24203a0-3d8b-11e4-8e77-7ba23226dee9'
    entity_count = 11

    def setUp(self):
        self.client = CoredataClient(
            host=self.host, auth=(self.username, self.password))
