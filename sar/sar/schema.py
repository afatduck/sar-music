import graphene
from graphene_django.types import DjangoObjectType
from music_api.models import Album, Comment, Song, Track, Updates

class TrackType(DjangoObjectType):
    class Meta:
        model = Track

class SongType(DjangoObjectType):
    released_ago = graphene.String()
    track_number = graphene.Int()

    class Meta:
        model = Song
        exclude = ('track_set',)

    def resolve_released_ago(self, info):
        return self.released_ago
    
    def resolve_track_number(self, info):
        return Track.objects.get(song_id=self.id, album_id=self.album_id).track_number

    
class AlbumType(DjangoObjectType):
    released_ago = graphene.String()
    duration = graphene.Int()
    released = graphene.Boolean()
    songs = graphene.List(SongType)
    number_of_songs = graphene.Int()

    class Meta:
        model = Album
        exclude = ('song_set',)

    def resolve_released_ago(self, info):
        return self.released_ago
    
    def resolve_duration(self, info):
        return self.duration
    
    def resolve_released(self, info):
        return self.released
    
    def resolve_songs(self, info):
        songs = Song.objects.filter(albums=self.id)
        for song in songs:
            song.album_id = self.id
        return songs
    
    def resolve_number_of_songs(self, info):
        return Song.objects.filter(albums=self.id).count()
    
class CommentType(DjangoObjectType):
    class Meta:
        model = Comment

class UpdatesType(DjangoObjectType):
    class Meta:
        model = Updates

class ModifySong(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        title = graphene.String(None)
        note = graphene.String(None)
        lyrics = graphene.String(None)
        albums = graphene.List(graphene.Int,None)
        alternatives = graphene.List(graphene.Int,None)
        features = graphene.String(None)
        youtube = graphene.String(None)
    
    song = graphene.Field(SongType)

    def mutate(self, info, id, title, note, lyrics, albums, features, alternatives, youtube):
        if not info.context.user.is_authenticated or not info.context.user.is_superuser:
            raise Exception('You must be a superuser to modify a song')

        song = Song.objects.get(pk=id)

        if title is not None:
            song.title = title

        if note is not None:
            song.note = note

        if lyrics is not None:
            song.lyrics = lyrics

        if features is not None:
            song.features = features

        if youtube is not None:
            song.youtube = youtube

        if albums is not None:
            song.albums.clear()
            for album in albums:
                song.albums.add(Album.objects.get(pk=album))

        if alternatives is not None:
            song.alternatives.clear()
            for alternative in alternatives:
                song.alternatives.add(Song.objects.get(pk=alternative))

        song.save()
        return ModifySong(song=song)
    
class ModifyAlbum(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        title = graphene.String(None)
        note = graphene.String(None)
        release_date = graphene.Date(None)
        ep = graphene.Boolean(None)
        alternatives = graphene.List(graphene.Int,None)
        youtube = graphene.String(None)
    
    album = graphene.Field(AlbumType)

    def mutate(self, info, id, title, note, release_date, ep, alternatives, youtube):
        if not info.context.user.is_authenticated or not info.context.user.is_superuser:
            raise Exception('You must be a superuser to modify an album')

        album = Album.objects.get(pk=id)

        if title is not None:
            album.title = title

        if note is not None:
            album.note = note

        if release_date is not None:
            album.release_date = release_date

        if ep is not None:
            album.ep = ep

        if youtube is not None:
            album.youtube = youtube

        if alternatives is not None:
            album.alternatives.clear()
            for alternative in alternatives:
                album.alternatives.add(Album.objects.get(pk=alternative))

        album.save()
        return ModifyAlbum(album=album)

class MakeAlbum(graphene.Mutation):
    class Arguments:
        title = graphene.String()
        note = graphene.String(None)
        release_date = graphene.Date(None)
        ep = graphene.Boolean(False)
        alternatives = graphene.List(graphene.Int, [])
        youtube = graphene.String(None)
    
    album = graphene.Field(AlbumType)

    def mutate(self, info, title, note, release_date, ep, alternatives, youtube):
        if not info.context.user.is_authenticated or not info.context.user.is_superuser:
            raise Exception('You must be a superuser to make an album')

        album = Album(title=title, note=note, release_date=release_date, ep=ep, youtube=youtube)
        album.save()

        for alternative in alternatives:
            album.alternatives.add(Album.objects.get(pk=alternative))

        album.save()
        return MakeAlbum(album=album)

class MakeUpdate(graphene.Mutation):
    class Arguments:
        title = graphene.String()
        content = graphene.String()
        songs = graphene.List(graphene.Int, [])
        albums = graphene.List(graphene.Int, [])
    
    update = graphene.Field(UpdatesType)

    def mutate(self, info, title, content, songs, albums):
        if not info.context.user.is_authenticated or not info.context.user.is_superuser:
            raise Exception('You must be a superuser to make an update')

        update = Updates(title=title, content=content)
        update.save()

        for song in songs:
            update.references_songs.add(Song.objects.get(pk=song))

        for album in albums:
            update.references_albums.add(Album.objects.get(pk=album))

        update.save()
        return MakeUpdate(update=update)

class MakeComment(graphene.Mutation):
    class Arguments:
        text = graphene.String()
        nickname = graphene.String()
        song = graphene.Int()
    
    comment = graphene.Field(CommentType)

    def mutate(self, info, text, nickname, song):
        comment = Comment(text=text, nickname=nickname, song=Song.objects.get(pk=song))
        comment.save()
        return MakeComment(comment=comment)

class DeleteSong(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
    
    song = graphene.Field(SongType)

    def mutate(self, info, id):
        if not info.context.user.is_authenticated or not info.context.user.is_superuser:
            raise Exception('You must be a superuser to delete a song')

        song = Song.objects.get(pk=id)
        song.delete()
        return DeleteSong(song=song)

class DeleteAlbum(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
    
    album = graphene.Field(AlbumType)

    def mutate(self, info, id):
        if not info.context.user.is_authenticated or not info.context.user.is_superuser:
            raise Exception('You must be a superuser to delete an album')

        album = Album.objects.get(pk=id)
        album.delete()
        return DeleteAlbum(album=album)

class DeleteComment(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
    
    comment = graphene.Field(CommentType)

    def mutate(self, info, id):
        if not info.context.user.is_authenticated or not info.context.user.is_superuser:
            raise Exception('You must be a superuser to delete a comment')

        comment = Comment.objects.get(pk=id)
        comment.delete()
        return DeleteComment(comment=comment)

class DeleteUpdate(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
    
    update = graphene.Field(UpdatesType)

    def mutate(self, info, id):
        if not info.context.user.is_authenticated or not info.context.user.is_superuser:
            raise Exception('You must be a superuser to delete an update')

        update = Updates.objects.get(pk=id)
        update.delete()
        return DeleteUpdate(update=update)

class Query(graphene.ObjectType):
    all_my_models = graphene.List(SongType)
    all_songs = graphene.List(SongType)
    all_albums = graphene.List(AlbumType)
    song = graphene.Field(SongType, id=graphene.Int())
    album = graphene.Field(AlbumType, id=graphene.Int())
    updates = graphene.List(UpdatesType, start=graphene.Int(0), count=graphene.Int())

    def resolve_all_albums(self, info, **kwargs):
        return Album.objects.all()

    def resolve_all_songs(self, info, **kwargs):
        return Song.objects.all()

    def resolve_all_my_models(self, info, **kwargs):
        return Song.objects.all()
    
    def resolve_song(self, info, **kwargs):
        id = kwargs.get('id')
        if id is not None:
            return Song.objects.get(pk=id)
        return None
    
    def resolve_album(self, info, **kwargs):
        id = kwargs.get('id')
        if id is not None:
            return Album.objects.get(pk=id)
        return None
    
    def resolve_updates(self, info, **kwargs):
        count = kwargs.get('count')
        start = kwargs.get('start')
        # sort by date
        if count is not None:
            return Updates.objects.order_by('-date')[start:count]
        return Updates.objects.order_by('-date')[start:]

class Mutation(graphene.ObjectType):
    modify_song = ModifySong.Field()
    modify_album = ModifyAlbum.Field()
    make_update = MakeUpdate.Field()
    make_comment = MakeComment.Field()
    delete_song = DeleteSong.Field()
    delete_album = DeleteAlbum.Field()
    delete_comment = DeleteComment.Field()
    delete_update = DeleteUpdate.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
