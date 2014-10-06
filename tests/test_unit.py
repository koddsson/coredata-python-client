import glob
import json
import httpretty

from nose.tools import raises
from unittest import TestCase, SkipTest, skip
from coredata import CoredataClient, Entity, CoredataError


def skipIfInList(action):
    def test_decorator(test_method):
        def test_decorated(self, *args, **kwargs):
            if action in self.skip_list:
                msg = ('Action: "{action}" not supported by Coredata for '
                       '{entity}.').format(action=action, entity=self.entity)
                raise SkipTest(msg)
            test_method(self)
        return test_decorated
    return test_decorator


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
        - Add tests for DELETE.
        - Add tests for DELETE error.
        - Add tests for PUT.
        - Add tests for PUT error.
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

    @skipIfInList('create')
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
    @skipIfInList('create')
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

    @skipIfInList('get')
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
    @skipIfInList('get')
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
        responses = []
        file_path = 'tests/json/get_all_{entity}*.json'.format(
            entity=self.entity.value)
        for f in sorted(glob.glob(file_path)):
            responses.append(httpretty.Response(body=open(f).read()))
        httpretty.register_uri(
            httpretty.GET,
            self.create_url(self.entity),
            responses=responses,
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

    @skipIfInList('delete')
    def test_deleting_a_entity(self):
        httpretty.register_uri(
            httpretty.DELETE,
            self.create_url(self.entity, self.entity_id),
            content_type="application/json; charset=utf-8")
        self.client.delete(self.entity, self.entity_id)
        # TODO. Assert is deleted.

    @raises(CoredataError)
    @skipIfInList('delete')
    def test_deleting_a_entity_error(self):
        httpretty.register_uri(
            httpretty.DELETE,
            self.create_url(self.entity, self.entity_id),
            status=500,
            body=json.dumps({'error_message': 'No way, Jose'}),
            content_type="application/json; charset=utf-8")
        self.client.delete(self.entity, self.entity_id)
        # TODO: Assert error message

    @skipIfInList('edit')
    def test_editing_a_entity(self):
        httpretty.register_uri(
            httpretty.GET,
            self.create_url(self.entity, self.entity_id),
            responses=[
                httpretty.Response(
                    body=open('tests/json/get_single_{entity}.json'.format(
                        entity=self.entity.value)).read()),
                httpretty.Response(
                    body=open('tests/json/edit_{entity}.json'.format(
                        entity=self.entity.value)).read())
            ],
            content_type="application/json; charset=utf-8")
        httpretty.register_uri(
            httpretty.PUT,
            self.create_url(self.entity, self.entity_id),
            status=204,
            content_type="application/json; charset=utf-8")
        files = self.client.get(self.entity, self.entity_id)
        self.assertEqual(len(files['objects']), 1)
        files['objects'][0]['title'] = 'All your base are belong to us'
        self.client.edit(self.entity, self.entity_id, files['objects'][0])
        edited_file = self.client.get(self.entity, self.entity_id)
        self.assertEqual(files, edited_file)

    @raises(CoredataError)
    @skipIfInList('edit')
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


@httpretty.activate
class TestComments(TestCase, EntityTestCase):
    entity = Entity.Comments
    entity_id = 'f24203a0-3d8b-11e4-8e77-7ba23226dee9'
    entity_count = 1
    skip_list = ['delete', 'edit']

    def setUp(self):
        self.client = CoredataClient(
            host=self.host, auth=(self.username, self.password))


@httpretty.activate
class TestContacts(TestCase, EntityTestCase):
    entity = Entity.Contacts
    entity_id = 'f24203a0-3d8b-11e4-8e77-7ba23226dee9'
    entity_count = 11
    skip_list = []

    def setUp(self):
        self.client = CoredataClient(
            host=self.host, auth=(self.username, self.password))

    def test_get_contact_files(self):
        """ GET /api/v2/contacts/{id}/files/ """
        # TODO: Get some better data here.
        httpretty.register_uri(
            httpretty.GET,
            self.create_url(self.entity, self.entity_id, Entity.Files),
            body=open('tests/json/empty.json').read(),
            content_type="application/json; charset=utf-8")
        entities = self.client.get(self.entity, self.entity_id, Entity.Files)
        self.assertEqual(len(entities), 0)

    def test_get_contact_projects(self):
        """ GET /api/v2/contacts/{id}/projects/ """
        httpretty.register_uri(
            httpretty.GET,
            self.create_url(self.entity, self.entity_id, Entity.Projects),
            body=open('tests/json/empty.json').read(),
            content_type="application/json; charset=utf-8")
        entities = self.client.get(
            self.entity, self.entity_id, Entity.Projects)
        self.assertEqual(len(entities), 0)

    def test_get_contact_tasks(self):
        """ GET /api/v2/contacts/{id}/tasks/ """
        httpretty.register_uri(
            httpretty.GET,
            self.create_url(self.entity, self.entity_id, Entity.Tasks),
            body=open('tests/json/empty.json').read(),
            content_type="application/json; charset=utf-8")
        entities = self.client.get(self.entity, self.entity_id, Entity.Tasks)
        self.assertEqual(len(entities), 0)


@httpretty.activate
@skip('Getting all docs through endpoint is broken')
class TestDocs(TestCase, EntityTestCase):
    entity = Entity.Docs
    entity_id = 'f24203a0-3d8b-11e4-8e77-7ba23226dee9'
    entity_count = 11
    skip_list = ['create', 'edit']

    def setUp(self):
        self.client = CoredataClient(
            host=self.host, auth=(self.username, self.password))


@httpretty.activate
class TestDynatypes(TestCase, EntityTestCase):
    entity = Entity.Dynatypes
    entity_id = '321b90be-3d8b-11e4-8d3e-e72bce805abc'
    entity_count = 20
    skip_list = ['create', 'edit', 'delete']

    def setUp(self):
        self.client = CoredataClient(
            host=self.host, auth=(self.username, self.password))


@httpretty.activate
class TestFiles(TestCase, EntityTestCase):
    entity = Entity.Files
    entity_id = '4ab3bb32-3e72-11e4-bfaa-ebeae41148db'
    entity_count = 45
    skip_list = []

    def setUp(self):
        self.client = CoredataClient(
            host=self.host, auth=(self.username, self.password))

    def test_getting_content(self):
        # TODO: There is a better way to do this.
        returned_content = open('tests/files/get_file', 'rb').read()
        httpretty.register_uri(
            httpretty.GET,
            self.create_url(Entity.Files, self.entity_id, Entity.Content),
            body=returned_content
        )

        content = self.client.get(Entity.Files, self.entity_id, Entity.Content)
        self.assertEqual(content, returned_content)

    @skip('Unable to test in swagger UI!')
    def test_editing_content(self):
        httpretty.register_uri(
            httpretty.PUT,
            self.create_url(Entity.Files, self.entity_id, Entity.Content),
            status=204
        )

        self.client.edit(
            Entity.Files, self.entity_id, Entity.Content, payload='hey')

    def test_getting_files_with_filtering(self):
        httpretty.register_uri(
            httpretty.GET,
            self.create_url(Entity.Files),
            body=open('tests/json/get_files_filtering.json').read(),
            content_type="application/json; charset=utf-8")
        r = self.client.get(
            Entity.Files, search_terms={'title__startswith': 'Y'})
        self.assertEqual(len(r), 6)


@httpretty.activate
class TestNav(TestCase, EntityTestCase):
    entity = Entity.Nav
    entity_id = 'f24203a0-3d8b-11e4-8e77-7ba23226dee9'
    entity_count = 1
    skip_list = ['create', 'edit', 'get', 'delete']

    def setUp(self):
        self.client = CoredataClient(
            host=self.host, auth=(self.username, self.password))

    @skip('Seems broken in the API itself')
    def test_getting_by_name(self):
        name = 'awesome_name'
        httpretty.register_uri(
            httpretty.GET,
            self.create_url(self.entity, name),
            body=open('tests/json/get_all_nav.json').read(),
            content_type="application/json; charset=utf-8")
        entities = self.client.get(self.entity, name)
        self.assertEqual(len(entities['objects'][0]['entries']), 1)


@httpretty.activate
class TestProjects(TestCase, EntityTestCase):
    """
    Unit tests for /projects/ endpoint.
    """
    entity = Entity.Projects
    entity_id = 'f24203a0-3d8b-11e4-8e77-7ba23226dee9'
    entity_count = 20
    skip_list = []

    def setUp(self):
        self.client = CoredataClient(
            host=self.host, auth=(self.username, self.password))

    def test_get_project_files(self):
        """ GET /api/v2/projects/{id}/files/ """
        # TODO: Get some better data here.
        httpretty.register_uri(
            httpretty.GET,
            self.create_url(self.entity, self.entity_id, Entity.Files),
            body=open('tests/json/empty.json').read(),
            content_type="application/json; charset=utf-8")
        entities = self.client.get(self.entity, self.entity_id, Entity.Files)
        self.assertEqual(len(entities), 0)

    @skip('Client doesn\'t support sub-sub-entities yet')
    def test_get_project_file_templates(self):
        """ GET /api/v2/projects/{id}/files/templates/ """
        # TODO: Get some better data here.
        httpretty.register_uri(
            httpretty.GET,
            self.create_url(
                self.entity, self.entity_id, Entity.Files, 'templates'),
            body=open('tests/json/empty.json').read(),
            content_type="application/json; charset=utf-8")
        entities = self.client.get(
            self.entity, self.entity_id, Entity.Files, 'templates')
        self.assertEqual(len(entities), 0)

    def test_get_project_tasks(self):
        """ GET /api/v2/project/{id}/tasks/ """
        httpretty.register_uri(
            httpretty.GET,
            self.create_url(self.entity, self.entity_id, Entity.Tasks),
            body=open('tests/json/empty.json').read(),
            content_type="application/json; charset=utf-8")
        entities = self.client.get(self.entity, self.entity_id, Entity.Tasks)
        self.assertEqual(len(entities), 0)

    @skip('Client doesn\'t support sub-sub-entities yet')
    def test_get_project_tasks_templates(self):
        """ GET /api/v2/project/{id}/tasks/templates """
        httpretty.register_uri(
            httpretty.GET,
            self.create_url(
                self.entity, self.entity_id, Entity.Tasks, 'templates'),
            body=open('tests/json/empty.json').read(),
            content_type="application/json; charset=utf-8")
        entities = self.client.get(
            self.entity, self.entity_id, Entity.Tasks, 'templates')
        self.assertEqual(len(entities), 0)

    def test_getting_projects_with_filtering(self):
        httpretty.register_uri(
            httpretty.GET,
            self.create_url(Entity.Projects),
            body=open('tests/json/get_projects_filtered.json').read(),
            content_type="application/json; charset=utf-8")
        r = self.client.get(
            Entity.Projects, search_terms={'title__startswith': 'Y'})
        self.assertEqual(len(r), 1)


@httpretty.activate
class TestSpaces(TestCase, EntityTestCase):
    entity = Entity.Spaces
    entity_id = '023a02ca-3e73-11e4-8e50-7b146cbe6428'
    entity_count = 4
    skip_list = ['delete', 'edit', 'create']

    def setUp(self):
        self.client = CoredataClient(
            host=self.host, auth=(self.username, self.password))

    def test_get_spaces_files(self):
        """ GET /api/v2/spaces/{id}/files/ """
        # TODO: Get some better data here.
        httpretty.register_uri(
            httpretty.GET,
            self.create_url(self.entity, self.entity_id, Entity.Files),
            body=open('tests/json/empty.json').read(),
            content_type="application/json; charset=utf-8")
        entities = self.client.get(self.entity, self.entity_id, Entity.Files)
        self.assertEqual(len(entities), 0)

    @skip('Client doesn\'t support sub-sub-entities yet')
    def test_get_spaces_files_templates(self):
        """ GET /api/v2/spaces/{id}/files/templates/ """
        # TODO: Get some better data here.
        httpretty.register_uri(
            httpretty.GET,
            self.create_url(
                self.entity, self.entity_id, Entity.Files, 'templates'),
            body=open('tests/json/empty.json').read(),
            content_type="application/json; charset=utf-8")
        entities = self.client.get(
            self.entity, self.entity_id, Entity.Files, 'templates')
        self.assertEqual(len(entities), 0)

    def test_get_space_projects(self):
        """" GET /api/v2/spaces/{id}/projects/ """
        httpretty.register_uri(
            httpretty.GET,
            self.create_url(self.entity, self.entity_id, Entity.Projects),
            body=open('tests/json/empty.json').read(),
            content_type="application/json; charset=utf-8")
        entities = self.client.get(
            self.entity, self.entity_id, Entity.Projects)
        self.assertEqual(len(entities), 0)

    @skip('Client doesn\'t support sub-sub-entities yet')
    def test_get_space_project_templates(self):
        """ GET /api/v2/spaces/{id}/projects/templates """
        httpretty.register_uri(
            httpretty.GET,
            self.create_url(
                self.entity, self.entity_id, Entity.Projects, 'templates'),
            body=open('tests/json/empty.json').read(),
            content_type="application/json; charset=utf-8")
        entities = self.client.get(
            self.entity, self.entity_id, Entity.Projects, 'templates')
        self.assertEqual(len(entities), 0)


@httpretty.activate
class TestTasks(TestCase, EntityTestCase):
    entity = Entity.Tasks
    entity_id = '9a8ddcf0-4746-11e4-b677-db026e61ad0a'
    entity_count = 4
    skip_list = []

    def setUp(self):
        self.client = CoredataClient(
            host=self.host, auth=(self.username, self.password))


@httpretty.activate
class TestUser(TestCase, EntityTestCase):
    entity = Entity.User
    entity_id = 'f24203a0-3d8b-11e4-8e77-7ba23226dee9'
    entity_count = 1
    skip_list = ['create', 'edit', 'get', 'delete']
    username = 'Administrator'

    def setUp(self):
        self.client = CoredataClient(
            host=self.host, auth=(self.username, self.password))

    def test_get_user_by_username(self):
        """ GET /api/v2/user/{username}/ """
        httpretty.register_uri(
            httpretty.GET,
            self.create_url(self.entity, self.username),
            body=open('tests/json/get_single_user.json').read(),
            content_type="application/json; charset=utf-8")
        entities = self.client.get(self.entity, self.username),
        self.assertEqual(len(entities), 1)

    def test_get_user_files(self):
        """ GET /api/v2/user/{username}/files/ """
        # TODO: Get some better data here.
        httpretty.register_uri(
            httpretty.GET,
            self.create_url(self.entity, self.username, Entity.Files),
            body=open('tests/json/empty.json').read(),
            content_type="application/json; charset=utf-8")
        entities = self.client.get(self.entity, self.username, Entity.Files)
        self.assertEqual(len(entities), 0)

    @skip('Client doesn\'t support sub-sub-entities yet')
    def test_get_user_files_templates(self):
        """ GET /api/v2/user/{id}/files/templates/ """
        # TODO: Get some better data here.
        httpretty.register_uri(
            httpretty.GET,
            self.create_url(
                self.entity, self.username, Entity.Files, 'templates'),
            body=open('tests/json/empty.json').read(),
            content_type="application/json; charset=utf-8")
        entities = self.client.get(
            self.entity, self.username, Entity.Files, 'templates')
        self.assertEqual(len(entities), 0)

    def test_get_user_tasks(self):
        """ GET /api/v2/user/{username}/tasks/ """
        httpretty.register_uri(
            httpretty.GET,
            self.create_url(self.entity, self.username, Entity.Tasks),
            body=open('tests/json/empty.json').read(),
            content_type="application/json; charset=utf-8")
        entities = self.client.get(self.entity, self.username, Entity.Tasks)
        self.assertEqual(len(entities), 0)

    def test_get_user_projects(self):
        """ GET /api/v2/user/{username}/projects/ """
        httpretty.register_uri(
            httpretty.GET,
            self.create_url(self.entity, self.username, Entity.Projects),
            body=open('tests/json/get_user_projects.json').read(),
            content_type="application/json; charset=utf-8")
        entities = self.client.get(self.entity, self.username, Entity.Projects)
        self.assertEqual(len(entities), 6)


@httpretty.activate
class TestUsers(TestCase, EntityTestCase):
    entity = Entity.Users
    entity_id = 'f24203a0-3d8b-11e4-8e77-7ba23226dee9'
    entity_count = 9
    skip_list = ['create', 'edit', 'get', 'delete']
    username = 'oskar'

    def setUp(self):
        self.client = CoredataClient(
            host=self.host, auth=(self.username, self.password))

    def test_get_users_by_username(self):
        """ GET /api/v2/users/{username}/ """
        httpretty.register_uri(
            httpretty.GET,
            self.create_url(self.entity, self.username),
            body=open('tests/json/get_single_users.json').read(),
            content_type="application/json; charset=utf-8")
        entities = self.client.get(self.entity, self.username),
        self.assertEqual(len(entities), 1)


@httpretty.activate
class TestValuelist(TestCase, EntityTestCase):
    entity = Entity.Valuelist
    entity_id = 'f24203a0-3d8b-11e4-8e77-7ba23226dee9'
    entity_count = 49
    skip_list = ['create', 'edit', 'get', 'delete']

    def setUp(self):
        self.client = CoredataClient(
            host=self.host, auth=(self.username, self.password))

    def test_getting_valuelist_by_name(self):
        httpretty.register_uri(
            httpretty.GET,
            self.create_url(self.entity, 'templates_labels'),
            body=open('tests/json/get_valuelist_by_name.json').read(),
            content_type="application/json; charset=utf-8")
        entities = self.client.get(self.entity, 'templates_labels')
        self.assertEqual(len(entities['objects'][0]['entries']), 28)
