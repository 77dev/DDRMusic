from django.urls import path
from  music_app.views import *


app_name = 'music_app'

urlpatterns = [

    path('', IndexView.as_view(), name='index'),

    path('register', register, name='register'),

    path('login_user', login_user, name='login_user'),

    path('logout_user', logout_user, name='logout_user'),

    # music/album_id
    path('<int:pk>/', DetailView.as_view(), name='detail'),

    # /music/album/add
    # path('album/add', AlbumCreate.as_view(), name='album_add'),

    path('album/add', create_album, name='album_add'),

    # music/album/2
    path('album/<int:pk>', AlbumUpdate.as_view(), name='album_update'),

    # music/album/2/delete
    path('album/<int:pk>/delete', AlbumDelete.as_view(), name='album_delete'),

    # favourite_album
    path('<int:pk>/favourite_album', favourite_album, name='favourite_album'),

    path('<int:pk>/create_song/', create_song, name='create_song'),

    # favourite_song
    path('<int:pk>/favourite_song', favourite_song, name='favourite_song'),

    # delete song
    path('<int:album_id>/delete_song/<int:song_id>', delete_song, name='delete_song'),

    # songs
    path('songs/<slug:filter_by>', songs, name='songs'),


]
