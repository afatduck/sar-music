from django.urls import path
from . import views

urlpatterns = [
    path('add-song/', views.AddSongView.as_view(), name='add-song'),
]