from rest_framework import serializers
from django.db import transaction, connection
from .models import TableStructure, TableFieldStructure, create_model


class DynamicModelSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'


class TableFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = TableFieldStructure
        fields = ('name', 'type')


class TableSerializer(serializers.ModelSerializer):
    fields = TableFieldSerializer(many=True)

    class Meta:
        model = TableStructure
        fields = ('name', 'fields')

    def create(self, validated_data: dict):
        try:
            with transaction.atomic():
                fields = validated_data.pop('fields')
                instance = TableStructure.objects.create(**validated_data)
                for field_data in fields:
                    field_data['table'] = instance
                    TableFieldStructure.objects.create(**dict(field_data))
                model = create_model(name=instance.name,
                                     fields=instance.get_field_dicts(),
                                     app_label='table',
                                     module='table.models')

                with connection.schema_editor() as schema_editor:
                    schema_editor.create_model(model)

                return model
        except Exception as e:
            raise serializers.ValidationError(e)

