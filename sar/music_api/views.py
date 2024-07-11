from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from google.cloud import storage
from decouple import config

from .models import Song, Album
from .serializers import SongSerializer, AlbumSerializer
from .utils import get_wav_file_duration

import uuid

# Create your views here.

class AddSongView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):

        if not request.user.is_superuser:
            return Response({
                "success": False,
                "message": "You are not authorized to perform this action."
            }, status=status.HTTP_401_UNAUTHORIZED)

        song_serializer = SongSerializer(data=request.data)
        if song_serializer.is_valid():
            
            artwork = song_serializer.validated_data['artwork']
            mp3 = song_serializer.validated_data['mp3']
            wav = song_serializer.validated_data['wav']
            flac = song_serializer.validated_data['flac']

            storage_client = storage.Client.from_service_account_json(config('GOOGLE_APPLICATION_CREDENTIALS'))
            bucket = storage_client.get_bucket('sar-music-bucket')

            blob_artwork = bucket.blob(f"artwork/song/{uuid.uuid4()}_{artwork.name}")
            blob_mp3 = bucket.blob(f"mp3/{mp3.name}")
            blob_wav = bucket.blob(f"wav/{wav.name}")
            blob_flac = bucket.blob(f"flac/{flac.name}")

            blob_artwork.upload_from_file(artwork)
            blob_mp3.upload_from_file(mp3)
            blob_wav.upload_from_file(wav)
            blob_flac.upload_from_file(flac)

            title = song_serializer.validated_data['title']
            release_date = song_serializer.validated_data['release_date'] if 'release_date' in song_serializer.validated_data else None
            note = song_serializer.validated_data['note'] if 'note' in song_serializer.validated_data else None
            lyrics = song_serializer.validated_data['lyrics'] if 'lyrics' in song_serializer.validated_data else None
            albums = song_serializer.validated_data['albums'] if 'albums' in song_serializer.validated_data else []
            alternatives = song_serializer.validated_data['alternatives'] if 'alternatives' in song_serializer.validated_data else []
            features = song_serializer.validated_data['features'] if 'features' in song_serializer.validated_data else None
            youtube = song_serializer.validated_data['youtube'] if 'youtube' in song_serializer.validated_data else None
            original = song_serializer.validated_data['original'] if 'original' in song_serializer.validated_data else True

            song = Song(
                title=title,
                note=note,
                lyrics=lyrics,
                features=features,
                youtube=youtube,
                artwork=blob_artwork.public_url,
                mp3=blob_mp3.public_url,
                wav=blob_wav.public_url,
                flac=blob_flac.public_url,
                original=original,
                duration=get_wav_file_duration(wav)
            )

            if release_date:
                song.release_date = release_date

            if albums:
                song.albumss.set(albums)

            if alternatives:
                song.alternatives.set(alternatives) 

            song.save()

            return Response({
                "success": True,
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(song_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddAlbumView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):

        if not request.user.is_superuser:
            return Response({
                "success": False,
                "message": "You are not authorized to perform this action."
            }, status=status.HTTP_401_UNAUTHORIZED)

        album_serializer = AlbumSerializer(data=request.data)
        if album_serializer.is_valid():
            
            artwork = album_serializer.validated_data['artwork']
            songs = album_serializer.validated_data['songs']

            storage_client = storage.Client.from_service_account_json(config('GOOGLE_APPLICATION_CREDENTIALS'))
            bucket = storage_client.get_bucket('sar-music-bucket')

            blob_artwork = bucket.blob(f"artwork/album/{uuid.uuid4()}_{artwork.name}")
            blob_artwork.upload_from_file(artwork)

            title = album_serializer.validated_data['title']
            release_date = album_serializer.validated_data['release_date'] if 'release_date' in album_serializer.validated_data else None
            note = album_serializer.validated_data['note'] if 'note' in album_serializer.validated_data else None
            youtube = album_serializer.validated_data['youtube'] if 'youtube' in album_serializer.validated_data else None

            album = Album(
                title=title,
                note=note,
                youtube=youtube,
                artwork=blob_artwork.public_url
            )

            if release_date:
                album.release_date = release_date

            album.save()

            if songs:
                album.songss.set(songs)

            return Response({
                "success": True,
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(album_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
