from rest_framework import serializers
from django.utils import timezone

from .models import Song, Album

class SongSerializer(serializers.Serializer):
    
    title = serializers.CharField(max_length=200)
    release_date = serializers.DateField(required=False, default=timezone.now().date())
    note = serializers.CharField(required=False)
    lyrics = serializers.CharField(required=False)
    albums = serializers.PrimaryKeyRelatedField(queryset=Album.objects.all(), required=False, many=True)
    alternatives = serializers.PrimaryKeyRelatedField(many=True, queryset=Song.objects.all(), required=False)
    features = serializers.CharField(required=False)
    youtube = serializers.URLField(required=False)
    artwork = serializers.ImageField(required=True)
    mp3 = serializers.FileField(required=True, allow_empty_file=False)
    wav = serializers.FileField(required=False, allow_empty_file=False)
    flac = serializers.FileField(required=False, allow_empty_file=False)
    original = serializers.BooleanField(default=True)

    class Meta:
        model = object

class AlbumSerializer(serializers.Serializer):
    
    title = serializers.CharField(max_length=200)
    release_date = serializers.DateField(required=False, default=timezone.now().date())
    original = serializers.BooleanField(default=True)
    youtube = serializers.URLField(required=False)
    artwork = serializers.ImageField(required=True)
    songs = serializers.PrimaryKeyRelatedField(many=True, queryset=Song.objects.all(), required=False)
    note = serializers.CharField(required=False)
    ep = serializers.BooleanField(default=False)
    alternatives = serializers.PrimaryKeyRelatedField(many=True, queryset=Album.objects.all(), required=False)

    class Meta:
        model = object