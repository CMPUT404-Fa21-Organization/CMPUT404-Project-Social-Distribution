from rest_framework import serializers

class ActivitySerializer(serializers.Serializer):
    actor = serializers.CharField()
    timestamp = serializers.DateTimeField()
    id = serializers.IntegerField()
    type = serializers.CharField()
    repo = serializers.CharField()