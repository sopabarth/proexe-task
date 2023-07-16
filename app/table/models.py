from django.db import models


def create_model(name, fields=None, app_label='', module='', options=None, admin_opts=None):
    """
    Create specified model
    """
    class Meta:
        # Using type('Meta', ...) gives a dictproxy error during model creation
        pass

    if app_label:
        # app_label must be set using the Meta inner class
        setattr(Meta, 'app_label', app_label)

    # Update Meta with any options that were provided
    if options is not None:
        for key, value in options.iteritems():
            setattr(Meta, key, value)

    # Set up a dictionary to simulate declarations within a class
    attrs = {'__module__': module, 'Meta': Meta}

    # Add in any fields that were provided
    if fields:
        attrs.update(fields)

    # Create the class, which automatically triggers ModelBase processing
    model = type(name, (models.Model,), attrs)

    return model


class TableStructure(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    def get_field_dicts(self) -> list:
        fields_dict = {}
        for item in self.fields.all():
            fields_dict.update(item.dict_repr)

        return fields_dict


# field_type_mapping = {
#     'integer': models.IntegerField,
#     'string': models.TextField,
#     'bool': models.BooleanField
# }
field_type_choices = [('integer', models.IntegerField()),
                      ('string', models.TextField()),
                      ('bool', models.BooleanField())]

field_type_mapping = {
        'string': models.CharField(),
        'integer': models.IntegerField(),
        'bool': models.BooleanField(),
    }


class TableFieldStructure(models.Model):
    table = models.ForeignKey(TableStructure, on_delete=models.CASCADE, related_name='fields')
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=field_type_choices)

    class Meta:
        unique_together = (('table', 'name',),)

    @property
    def dict_repr(self):
        return {self.name: field_type_mapping[self.type]}



