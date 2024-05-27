from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import Album, Song, Track

@receiver(m2m_changed, sender=Album.song_set.through)
def update_album_duration(sender, instance, action, **kwargs):
    if action == 'post_add':
        song_id = instance.id
        album_id = list(kwargs['pk_set'])[0]

        song = Song.objects.get(pk=song_id)
        album = Album.objects.get(pk=album_id)
        
        all_album_tracks = Track.objects.filter(album=album)
        all_album_tracks_count = all_album_tracks.count()

        newTrack = Track(album=album, song=song, track_number=all_album_tracks_count + 1)
        newTrack.save()

    elif action == 'post_remove':
        song_id = instance.id
        album_id = list(kwargs['pk_set'])[0]

        song = Song.objects.get(pk=song_id)
        album = Album.objects.get(pk=album_id)

        track = Track.objects.get(album = album, song=song)
        trackNumber = track.track_number
        track.delete()

        all_album_tracks = Track.objects.filter(album=album)
        for track in all_album_tracks:
            if track.track_number > trackNumber:
                track.track_number -= 1
                track.save()