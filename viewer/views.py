from django.shortcuts import render
from django.views.generic import ListView, DetailView

from viewer.models import Song, MusicGroupMembership


def home(request):
    return render(request, 'home.html')


class SongsListView(ListView):
    template_name = 'songs.html'
    model = Song
    context_object_name = 'songs'


class SongDetailView(DetailView):
    template_name = 'song.html'
    model = Song
    context_object_name = 'song'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        song = self.object

        performances = song.performances.select_related(
            'contributor', 'contributor_role', 'music_group', 'music_group_role'
        )

        contributors_by_category = {}
        groups_by_role = {}
        involved_music_groups = set()

        for perf in performances:
            # Contributors (people)
            if perf.contributor and perf.contributor_role:
                category = perf.contributor_role.category
                role_name = perf.contributor_role.name
                if category not in contributors_by_category:
                    contributors_by_category[category] = []
                contributors_by_category[category].append((perf.contributor, role_name))

            # Music Groups
            if perf.music_group and perf.music_group_role:
                role = perf.music_group_role.name
                if role not in groups_by_role:
                    groups_by_role[role] = []
                groups_by_role[role].append(perf.music_group)
                involved_music_groups.add(perf.music_group)

        # Remove duplicates for contributors
        for category, contribs in contributors_by_category.items():
            seen_ids = set()
            filtered = []
            for contributor, role_name in contribs:
                if contributor.id not in seen_ids:
                    filtered.append((contributor, role_name))
                    seen_ids.add(contributor.id)
            contributors_by_category[category] = filtered

        # Remove duplicates for music groups
        for role, groups in groups_by_role.items():
            unique_groups = []
            seen_ids = set()
            for group in groups:
                if group.id not in seen_ids:
                    unique_groups.append(group)
                    seen_ids.add(group.id)
            groups_by_role[role] = unique_groups

        # Members of involved music groups
        music_groups_with_members = []
        for group in involved_music_groups:
            members = MusicGroupMembership.objects.filter(
                music_group=group
            ).select_related('member')
            contributors = [m.member for m in members]
            music_groups_with_members.append({
                'group': group,
                'members': contributors
            })

        # Additional context
        album = song.albums.first()
        song_artists = song.artist.all()
        song_music_groups = song.music_group.all()

        context.update({
            'contributors_by_category': contributors_by_category,
            'groups_by_role': groups_by_role,
            'music_groups_with_members': music_groups_with_members,
            'album': album,
            'song_artists': song_artists,
            'song_music_groups': song_music_groups,
        })

        return context