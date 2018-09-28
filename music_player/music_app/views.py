from django.urls import reverse_lazy
from django.views import generic
from .models import *
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from .forms import *
from django.contrib.auth import logout


AUDIO_FILE_TYPES = ['wav', 'mp3', 'ogg']
IMAGE_FILE_TYPES = ['png', 'jpg', 'jpeg']


class IndexView(generic.ListView):

    template_name = 'music_app/index.html'
    context_object_name = 'all_albums'

    def get_queryset(self):
        return Album.objects.all()


class DetailView(generic.DetailView):

    model = Album
    template_name = 'music_app/detail.html'


# This is the way of creating through class based views and below  is correct

#
# class AlbumCreate(CreateView):
#
#     model = Album
#     fields = ['artist', 'album_title', 'genre', 'album_logo']
#
#     def form_valid(self, form):
#
#         model = form.save(commit=False)
#         model.user = self.request.user
#         model.save()
#         return render(self.request, 'music_app/index.html')
#
#     ''' here in this model form , we didn't explicitly specify any template name but it searches for the html form which has model name in
#     this case album_form.html because ot has the name of album'''
#     '''Refer this: https://docs.djangoproject.com/en/2.1/topics/class-based-views/generic-display/'''
#

def create_album(request):
    if not request.user.is_authenticated:
        return render(request, 'music_app/login.html')
    else:
        form = AlbumForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            album = form.save(commit=False)
            album.user = request.user
            album.album_logo = request.FILES['album_logo']
            file_type = album.album_logo.url.split('.')[-1]
            file_type = file_type.lower()
            if file_type not in IMAGE_FILE_TYPES:
                context = {
                    'album': album,
                    'form': form,
                    'error_message': 'Image file must be PNG, JPG, or JPEG',
                }
                return render(request, 'music_app/album_form.html', context)
            album.save()
            return render(request, 'music_app/detail.html', {'album': album})
        context = {
            "form": form,
        }
        return render(request, 'music_app/album_form.html', context)


class AlbumUpdate(UpdateView):

    model = Album
    fields = ['artist', 'album_title', 'genre', 'album_logo']


class AlbumDelete(DeleteView):
    model = Album
    success_url = reverse_lazy('music_app:index')


# class UserFormView(View):
#
#     import ipdb
#     ipdb.set_trace()
#
#     form_class = UserForm
#     template_name = 'music_app/registration_form.html'
#
#     # display blank form
#     def get(self, request):
#         form = self.form_class(None)
#         return redirect(request, self.template_name, {'form': form})
#
#     def post(self, request):
#
#         form = self.form_class(request.POST)
#
#         if form.is_valid():
#
#             user = form.save(commit=False)
#
#             # cleaned (normalized) data
#             username = form.cleaned_data['username']
#             password = form.cleaned_data['password']
#             user.set_password(password)
#             user.save()
#
#             # return user objects if credentials are correct
#             user = authenticate(username=username, password=password)
#
#             if user is not None:
#
#                 if user.is_active:
#                     login(request, user)
#                     return redirect('music_app:index')
#
#         return redirect(request, self.template_name, {'form': form})


def register(request):

    form = UserForm(request.POST or None)

    if form.is_valid():

        user = form.save(commit=False)
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user.set_password(password)
        user.save()
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                albums = Album.objects.all()
                return render(request, 'music_app/index.html', {'albums': albums})
    context = \
        {
            "form": form,
        }
    return render(request, 'music_app/registration_form.html', context)


def login_user(request):

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                albums = Album.objects.all()
                return render(request, 'music_app/index.html', {'all_albums': albums})
            else:
                return render(request, 'music_app/login.html', {'error_message': 'Your Account has disabled'})
        else:

            return render(request, 'music_app/login.html', {'error_message': 'Invalid Credentials'})

    return render(request, 'music_app/login.html')


def logout_user(request):

    logout(request)
    return redirect('music_app:login_user')


def favourite_song(request, pk):

    song = get_object_or_404(Song, pk=pk)
    try:
        if song.is_favourite:
            song.is_favourite = False
        else:
            song.is_favourite = True
        song.save()
    except (KeyError, Song.DoesNotExist):
        return redirect('music_app:detail', pk=song.album.id)
    else:
        return redirect('music_app:detail', pk=song.album.id)


def favourite_album(request, pk):

    album = get_object_or_404(Album, pk=pk)
    try:
        if album.is_favourite:
            album.is_favourite = False
        else:
            album.is_favourite = True
        album.save()
    except (KeyError, Album.DoesNotExist):
        return redirect('music_app:index')
    else:
        return redirect('music_app:index')


def create_song(request, pk):

    form = SongForm(request.POST or None, request.FILES or None)
    album = get_object_or_404(Album, pk=pk)
    if form.is_valid():
        albums_songs = album.song_set.all()
        for song in albums_songs:
            if song.song_title == form.cleaned_data.get("song_title"):
                context = {
                    'album': album,
                    'form': form,
                    'error_message': 'You already added that song',
                }
                return render(request, 'music_app/create_song.html', context)
        song = form.save(commit=False)
        song.album = album
        song.audio_file = request.FILES['audio_file']
        file_type = song.audio_file.url.split('.')[-1]
        file_type = file_type.lower()
        if file_type not in AUDIO_FILE_TYPES:
            context = {
                'album': album,
                'form': form,
                'error_message': 'Audio file must be WAV, MP3, or OGG',
            }
            return render(request, 'music_app/create_song.html', context)
        song.save()
        return render(request, 'music_app/detail.html', {'album': album})

    context = {
        'album': album,
        'form': form,
    }
    return render(request, 'music_app/create_song.html', context)


def delete_song(request, album_id, song_id):

    album = get_object_or_404(Album, pk=album_id)
    song = Song.objects.get(pk=song_id)
    song.delete()
    return render(request, 'music_app/detail.html', {'album' : album})


def songs(request, filter_by):

    if not request.user.is_authenticated:
        return render(request, 'music_app/login.html')
    else:
        try:
            song_ids = []
            for album in Album.objects.filter(user=request.user):
                for song in album.song_set.all():
                    song_ids.append(song.pk)
            users_songs = Song.objects.filter(pk__in=song_ids)
            if filter_by == 'favourites':
                users_songs = users_songs.filter(is_favourite=True)
        except Album.DoesNotExist:
            users_songs = []
        return render(request, 'music_app/songs.html', {
            'song_list': users_songs,
            'filter_by': filter_by,
        })


