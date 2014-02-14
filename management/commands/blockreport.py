import base64
import json
import urllib2
from urlparse import urljoin

from django.core.management.base import BaseCommand, CommandError

from hofbudget.models import Client, Project


# YTD since 2013-07-01
# Create your commands here
class Command(BaseCommand):
    help = 'Prints Clients Hours Blocks'

    def handle(self, *args, **options):
        api_token = '0cd32d2dedb4f1fbe5c3f23a284168e1'

        base_url = 'https://www.toggl.com/api/v8/workspaces/179261/'
        clients_url = urljoin(base_url, 'clients')
        projects_url = urljoin(base_url, 'projects')

        auth = base64.encodestring('{}:{}'.format(api_token, 'api_token'))[:-1]

        request = urllib2.Request(clients_url)
        request.add_header('Authorization', 'Basic {}'.format(auth))

        response = urllib2.urlopen(request)
        response = json.loads(response.read())

        clients = []

        for obj in response:
            client = Client(name=obj.get('name'), toggl_id=obj.get('id'))
            clients.append(client)

        Client.objects.bulk_create(clients)

        request = urllib2.Request(projects_url)
        request.add_header('Authorization', 'Basic {}'.format(auth))

        response = urllib2.urlopen(request)
        response = json.loads(response.read())

        projects = []

        for obj in response:
            if not obj.get('cid'):
                continue

            project = Project(name=obj.get('name'), toggl_id=obj.get('id'))
            project.client_id = obj.get('cid')

            projects.append(project)

        Project.objects.bulk_create(projects)

        self.stdout.write('CommonCode')
