from rest_framework import serializers


class FileDetailSerializer(serializers.Serializer):
    file = serializers.FileField()
    filename = serializers.CharField()
