from django.apps import apps
from django.db.backends.base.schema import BaseDatabaseSchemaEditor
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import create_model, TableStructure
from .serializers import TableSerializer, DynamicModelSerializer
from django.db import models, connection
import sys


@api_view(['POST'])
def generate_dynamic_model(request):
    serializer = TableSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
    return Response()


@api_view(['PUT'])
def update_dynamic_model(request):
    """
    Update dynamic model does not work, it is not finished
    :param request:
    :return:
    """
    table_structure = TableStructure.objects.get(id=id)
    model = create_model(name=table_structure.name,
                         fields=table_structure.get_field_dicts(),
                         app_label='table',
                         module='table.models')



    model = apps.get_model('table', 'ModelName')
    fields = request.data['fields']
    add_fields = {}
    for key in fields:
        match fields[key]:
            case 'string':
                fields[key] = models.CharField()
            case 'integer':
                fields[key] = models.IntegerField()
            case 'bool':
                fields[key] = models.BooleanField()
        try:
            getattr(model, key)
        except AttributeError:
            add_fields[key] = fields[key]

    for key in add_fields:
        fields.pop(key)

    with connection.schema_editor() as schema_editor:
        if fields:
            for key, value in fields.items():
                schema_editor.alter_field(model, getattr(model, key), value, strict=False)
        if add_fields:
            for key, value in add_fields.items():
                setattr(model, key, value)

                schema_editor.add_field(model, value)

    return Response()


@api_view(['POST'])
def add_row(request, id):
    table_structure = TableStructure.objects.get(id=id)
    model = create_model(name=table_structure.name,
                         fields=table_structure.get_field_dicts(),
                         app_label='table',
                         module='table.models')
    DynamicModelSerializer.Meta.model = model
    serializer = DynamicModelSerializer(data=request.data)
    # setattr(serializer.Meta, 'model', model)
    if serializer.is_valid():
        serializer.save()

    return Response()

@api_view(['GET'])
def list_rows(request, id):
    table_structure = TableStructure.objects.get(id=id)
    model = create_model(name=table_structure.name,
                         fields=table_structure.get_field_dicts(),
                         app_label='table',
                         module='table.models')
    model_data = model.objects.all()
    setattr(DynamicModelSerializer.Meta, 'model', model)
    serializer = DynamicModelSerializer(model_data, many=True)
    ret_data = serializer.data.copy()
    delattr(DynamicModelSerializer.Meta, 'model')

    return Response(ret_data)
