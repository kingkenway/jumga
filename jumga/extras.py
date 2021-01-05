from rest_framework.exceptions import PermissionDenied
from rest_framework import status
from django.db import models


class CharNullField(models.CharField):
    description = "CharField that stores NULL but returns ''"

    def from_db_value(self, value, expression, connection, context=None):
        """
        Gets value right out of the db and changes it if its ``None``.
        """
        return value or ''

    def to_python(self, value):
        if isinstance(value, models.CharField):
            return value
        return value or ''

    def get_prep_value(self, value):
        return value or None

# https://stackoverflow.com/questions/454436/unique-fields-that-allow-nulls-in-django


class MyCustomExcpetion(PermissionDenied):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Custom Exception Message"
    default_code = 'invalid'

    def __init__(self, detail, status_code=None):
        self.detail = detail
        if status_code is not None:
            self.status_code = status_code
