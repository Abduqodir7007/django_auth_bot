from rest_framework import serializers


class CodeSerializer(serializers.Serializer):
    code = serializers.IntegerField(required=True)