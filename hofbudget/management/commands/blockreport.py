import requests

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from hofbudget.models import Client, Project


# YTD since 2013-07-01
# Create your commands here
class Command(BaseCommand):
    help = 'Prints Clients Hours Blocks'

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.base_url = 'https://www.toggl.com/api/v8/workspaces/179261/'

    def _fetch_clients(self):
        request = requests.get(
            self.base_url + '/clients',
            headers={'content-type': 'application/json'},
            auth=requests.auth.HTTPBasicAuth(settings.TOGGL_TOKEN, 'api_token')
        )

        return request.json()

    def _fetch_projects(self):
        request = requests.get(
            self.base_url + '/projects',
            headers={'content-type': 'application/json'},
            auth=requests.auth.HTTPBasicAuth(settings.TOGGL_TOKEN, 'api_token')
        )

        return request.json()

    def _sync_clients(self):
        clients = []

        for obj in self._fetch_clients:
            client = Client(name=obj.get('name'), toggl_id=obj.get('id'))
            clients.append(client)

        Client.objects.bulk_create(clients)

    def _sync_projects(self):
        projects = []

        for obj in self._fetch_projects():
            if not obj.get('cid'):
                continue

            project = Project(name=obj.get('name'), toggl_id=obj.get('id'))
            project.client_id = obj.get('cid')

            projects.append(project)

        Project.objects.bulk_create(projects)

    def handle(self, *args, **options):
        self.stdout.write('CommonCode')
