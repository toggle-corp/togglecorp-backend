from django.db import models

from apps.common.models import UserResource
# Create your models here.


class Employee(UserResource):
    class DepartmentType(models.IntegerChoices):
        DEVELOPMENT = 1, 'Development'
        ANALYSIS = 2, 'Analysis'
        OPERATIONS = 3, 'Operations'
    employee_id = models.CharField(max_length=10)
    department = models.SmallIntegerField(unique=True, choices=DepartmentType.choices)
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    description = models.TextField()
    funny_description = models.TextField()
    linkedin_link = models.URLField(max_length=200, null=True, blank=True)
    github_link = models.URLField(max_length=200, null=True, blank=True)
    instagram_link = models.URLField(max_length=200, null=True, blank=True)
    facebook_link = models.URLField(max_length=200, null=True, blank=True)
    stackoverflow_link = models.URLField(max_length=200, null=True, blank=True)
    blog_link = models.URLField(max_length=200, null=True, blank=True)
    alumni = models.BooleanField(default=False)
