from django.contrib import admin
from .models import Song, Album, Comment, Updates, Track

admin.site.register(Song)
admin.site.register(Album)
admin.site.register(Comment)
admin.site.register(Updates)
admin.site.register(Track)

# Register your models here.
