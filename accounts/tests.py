from django.test import TestCase
from django.contrib.auth.models import User
from .models import Profile


class ProfileModelTest(TestCase):

    def test_create_profile_and_str(self):
        user = User.objects.create_user(username='testuser', password='12345')
        profile = Profile.objects.create(user=user)

        self.assertEqual(str(profile), 'testuser')
        self.assertEqual(profile.user, user)
