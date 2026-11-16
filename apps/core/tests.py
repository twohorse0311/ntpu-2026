from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from django.template.loader import render_to_string
from django.test import RequestFactory
from django.urls import reverse

from apps.accounts.models import UserProfile


class SharedNavbarTests(TestCase):
    def render_base_template(self, user):
        request = RequestFactory().get("/")
        request.user = user
        return render_to_string("core/base.html", request=request)

    def test_anonymous_home_shows_account_links_without_logout_controls(self):
        response = self.render_base_template(AnonymousUser())

        self.assertIn("我的房間", response)
        self.assertIn("登入", response)
        self.assertIn("註冊", response)
        self.assertNotIn("登出", response)

    def test_authenticated_home_shows_display_name_and_logout_control(self):
        user = get_user_model().objects.create_user(
            username="mahjong-dog", password="safe-test-password"
        )
        UserProfile.objects.create(user=user, display_name="麻將狗")
        response = self.render_base_template(user)

        self.assertIn("麻將狗", response)
        self.assertIn("登出", response)
        self.assertNotIn(">登入<", response)
        self.assertNotIn(">註冊<", response)

    def test_home_inherits_the_shared_navbar(self):
        response = self.client.get(reverse("core:home"))

        self.assertContains(response, "我的房間")
        self.assertContains(response, "登入")
        self.assertContains(response, "core/css/base.css")
        self.assertContains(response, "core/css/home.css")
