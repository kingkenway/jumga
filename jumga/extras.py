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
