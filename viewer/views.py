from django.shortcuts import render

from viewer.models import Song


def home(request):
    return render(request, 'home.html')


def songs(request):
    songs_list = Song.objects.all()
    context = {'songs': songs_list}
    return render(request, 'songs.html', context)
