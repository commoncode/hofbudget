from urllib import urlencode

import requests

from django.core.management.base import BaseCommand
from django.conf import settings

from hofbudget.models import Client, Project


# Create your commands here
class Command(BaseCommand):
    help = 'Prints Clients Hours Blocks'

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.base_url = 'https://www.toggl.com/api/v8/workspaces/{}/'.format(
            settings.TOGGL_WORKSPACE)

    def _fetch(self, kind):
        return requests.get(self.base_url + kind,
            auth=requests.auth.HTTPBasicAuth(settings.TOGGL_TOKEN, 'api_token')
        ).json()

    def _sync_clients(self):
        Client.objects.all().delete()
        clients = []

        for obj in self._fetch('clients'):
            client = Client(name=obj.get('name'), toggl_id=obj.get('id'))
            clients.append(client)

        Client.objects.bulk_create(clients)

    def _sync_projects(self):
        Project.objects.all().delete()
        projects = []

        for obj in self._fetch('projects'):
            if not obj.get('cid'):
                continue

            project = Project(name=obj.get('name'), toggl_id=obj.get('id'))
            project.client_id = obj.get('cid')

            projects.append(project)

        Project.objects.bulk_create(projects)

    def handle(self, *args, **options):
        self._sync_clients()
        self._sync_projects()

        client_ids = ','.join(map(str, Client.objects.all().values_list(
            'toggl_id', flat=True)))
        project_ids = ','.join(map(str, Project.objects.all().values_list(
            'toggl_id', flat=True)))

        params = '?{}'.format(urlencode({
            'user_agent': 'hofbudget',
            'workspace_id': settings.TOGGL_WORKSPACE,
            'since': '2013-07-01',
            'client_ids': client_ids,
            'project_ids': project_ids
        }))

        request = requests.get(
            'https://toggl.com/reports/api/v2/summary' + params,
            auth=requests.auth.HTTPBasicAuth(settings.TOGGL_TOKEN, 'api_token')
        ).json()

        total = request.get('total_grand') / (1000.0 * 60.0 * 60.0)

        self.stdout.write(str(total))
