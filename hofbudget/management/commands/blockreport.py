from urllib import urlencode

import requests

from django.core.management.base import BaseCommand
from django.conf import settings

from hofbudget.models import Client, Project


def to_hours(milliseconds):
    return milliseconds / (1000.0 * 60.0 * 60.0)


# Create your commands here
class Command(BaseCommand):
    help = u'Prints Clients Hours Blocks'

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.base_url = u'https://www.toggl.com/api/v8/workspaces/{}/'.format(
            settings.TOGGL_WORKSPACE)

    def _fetch(self, kind):
        return requests.get(self.base_url + kind,
            auth=requests.auth.HTTPBasicAuth(settings.TOGGL_TOKEN, 'api_token')
        ).json()

    def _sync_clients(self):
        Client.objects.all().delete()
        clients = []

        for obj in self._fetch(u'clients'):
            client = Client(name=obj.get(u'name'), toggl_id=obj.get('id'))
            clients.append(client)

        Client.objects.bulk_create(clients)

    def _sync_projects(self):
        Project.objects.all().delete()
        projects = []

        for obj in self._fetch(u'projects'):
            if not obj.get(u'cid'):
                continue

            project = Project(name=obj.get(u'name'), toggl_id=obj.get('id'))
            project.client_id = obj.get(u'cid')

            projects.append(project)

        Project.objects.bulk_create(projects)

    def handle(self, *args, **options):
        self._sync_clients()
        self._sync_projects()

        client_ids = u','.join(map(str, Client.objects.all().values_list(
            u'toggl_id', flat=True)))
        project_ids = u','.join(map(str, Project.objects.all().values_list(
            u'toggl_id', flat=True)))

        params = urlencode({
            u'user_agent': 'hofbudget',
            u'workspace_id': settings.TOGGL_WORKSPACE,
            u'since': '2013-07-01',
            u'client_ids': client_ids,
            u'project_ids': project_ids,
            u'task_ids': 0
        })

        request = requests.get(
            u'https://toggl.com/reports/api/v2/summary?' + params,
            auth=requests.auth.HTTPBasicAuth(settings.TOGGL_TOKEN, 'api_token')
        ).json()

        total = to_hours(request.get(u'total_grand'))

        clients = {
            u'total': total
        }

        for obj in request.get(u'data'):
            name = obj.get(u'title').get(u'client')
            time = to_hours(obj.get(u'time'))

            client = clients.get(name)

            if client:
                client += time
            else:
                clients[name] = time

        from pprint import pprint
        pprint(clients)
