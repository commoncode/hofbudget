from django.db import models


# Create your models here.
class Client(models.Model):
    name = models.CharField(max_length=90)
    toggl_id = models.PositiveSmallIntegerField(primary_key=True)
    time = models.PositiveIntegerField(default=0)

    def __unicode__(self):
        return self.name


class Project(models.Model):
    client = models.ForeignKey('Client', related_name='projects')
    estimated = models.PositiveIntegerField(default=0)
    name = models.CharField(max_length=90)
    toggl_id = models.PositiveSmallIntegerField(primary_key=True)

    def __unicode__(self):
        return self.name
