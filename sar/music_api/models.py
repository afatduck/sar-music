from django.utils import timezone
from django.db import models

class SA(models.Model):
    title = models.CharField(max_length=100)
    artwork = models.URLField()
    release_date = models.DateField(null=True)
    original = models.BooleanField(default=True)
    youtube = models.URLField(null=True)

    def __str__(self):
        return self.title

    @property
    def released_ago(self):
        days = (timezone.now().date() - self.release_date).days
        if days == 0:
            return 'Today'
        elif days == 1:
            return 'Yesterday'
        elif days < 31:
            return f'{days} days ago'
        elif days < 365:
            return f'{days // 30} months ago'
        else:
            return f'{days // 365} years ago'
        
    class Meta:
        abstract = True

class Album(SA):
    ep = models.BooleanField(default=False)
    alternatives = models.ManyToManyField('self', blank=True)

    @property
    def duration(self):
        return sum([song.duration for song in self.song_set.all()])

    @property
    def released(self):
        return self.release_date is not None


class Song(SA):
    note = models.TextField(null=True)
    mp3 = models.URLField()
    wav = models.URLField()
    flac = models.URLField()
    duration = models.IntegerField(default=0)
    lyrics = models.TextField(null=True, blank=True)
    albums = models.ManyToManyField(Album, blank=True)
    alternatives = models.ManyToManyField('self', blank=True)
    features = models.TextField(null=True, blank=True)

class Comment(models.Model):
    text = models.TextField()
    date = models.DateField(auto_now=True)
    nickname = models.CharField(max_length=100)
    song = models.ForeignKey(Song, on_delete=models.CASCADE)

class Updates(models.Model):
    title = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now=True)
    content = models.TextField()
    references_songs = models.ManyToManyField(Song, blank=True)
    references_albums = models.ManyToManyField(Album, blank=True)
    
class Track(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    track_number = models.IntegerField()