from django.contrib.auth import get_user_model
from django.db import transaction
from django.test import TestCase, override_settings
from django.urls import reverse
from redis.exceptions import RedisError
from unittest.mock import patch

from apps.accounts.models import UserProfile

from .models import Room


@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
)
class RoomListApiTests(TestCase):
    def setUp(self):
        from django.core.cache import cache

        cache.clear()
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(
            username="owner", password="safe-test-password"
        )
        self.other_owner = user_model.objects.create_user(
            username="other", password="safe-test-password"
        )
        UserProfile.objects.create(user=self.owner, display_name="房主")
        UserProfile.objects.create(user=self.other_owner)
        self.url = reverse("majon:room-list-data")

    def create_room(self, owner, name, index):
        return Room.objects.create(owner=owner, name=name, code=f"R{index:03d}")

    def test_unauthenticated_request_returns_json_401(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response["Content-Type"], "application/json")

    def test_returns_only_the_current_users_rooms_in_newest_first_order(self):
        older_room = self.create_room(self.owner, "較早房間", 1)
        newer_room = self.create_room(self.owner, "較新房間", 2)
        self.create_room(self.other_owner, "其他人的房間", 3)
        self.client.force_login(self.owner)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["total_count"], 2)
        self.assertEqual(
            [item["id"] for item in payload["items"]],
            [newer_room.id, older_room.id],
        )
        self.assertEqual(payload["items"][0]["owner_display_name"], "房主")
        self.assertEqual(
            payload["items"][0]["detail_url"],
            reverse("majon:room-detail", kwargs={"room_id": newer_room.id}),
        )

    def test_search_paginates_and_returns_the_documented_shape(self):
        for index in range(12):
            self.create_room(self.owner, f"Friday {index}", index + 10)
        self.create_room(self.owner, "Saturday game", 99)
        self.client.force_login(self.owner)

        response = self.client.get(self.url, {"q": "  friday  ", "page": 1})

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(len(payload["items"]), 10)
        self.assertEqual(payload["page"], 1)
        self.assertEqual(payload["page_size"], 10)
        self.assertEqual(payload["total_count"], 12)
        self.assertEqual(payload["total_pages"], 2)
        self.assertFalse(payload["has_previous"])
        self.assertTrue(payload["has_next"])
        self.assertTrue(
            {"id", "name", "code", "owner_display_name", "detail_url"}
            .issubset(payload["items"][0])
        )

    def test_invalid_pages_normalize_to_first_and_high_pages_to_last(self):
        for index in range(12):
            self.create_room(self.owner, f"Room {index}", index + 30)
        self.client.force_login(self.owner)

        for invalid_page in ("abc", "0"):
            response = self.client.get(self.url, {"page": invalid_page})
            self.assertEqual(response.json()["page"], 1)

        final_page_response = self.client.get(self.url, {"page": 99})
        final_page_payload = final_page_response.json()
        self.assertEqual(final_page_payload["page"], 2)
        self.assertEqual(len(final_page_payload["items"]), 2)
        self.assertTrue(final_page_payload["has_previous"])
        self.assertFalse(final_page_payload["has_next"])


@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
)
class RoomListCacheTests(TestCase):
    def setUp(self):
        from django.core.cache import cache

        cache.clear()
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(username="cached-owner")
        self.other_owner = user_model.objects.create_user(username="other-owner")
        UserProfile.objects.create(user=self.owner)
        UserProfile.objects.create(user=self.other_owner)
        self.url = reverse("majon:room-list-data")

    def test_same_request_uses_cached_payload_and_keys_isolate_owner_query_and_page(self):
        from .cache import build_room_list_cache_key

        Room.objects.create(owner=self.owner, name="Friday game", code="CACHE-1")
        self.client.force_login(self.owner)
        first = self.client.get(self.url, {"q": " friday ", "page": 1})
        with patch("apps.majon.views.Room.objects.select_related") as query:
            second = self.client.get(self.url, {"q": "friday", "page": 1})

        self.assertEqual(second.json(), first.json())
        query.assert_not_called()
        self.assertNotEqual(
            build_room_list_cache_key(self.owner.id, "friday", 1),
            build_room_list_cache_key(self.other_owner.id, "friday", 1),
        )
        self.assertNotEqual(
            build_room_list_cache_key(self.owner.id, "friday", 1),
            build_room_list_cache_key(self.owner.id, "other", 1),
        )
        self.assertNotEqual(
            build_room_list_cache_key(self.owner.id, "friday", 1),
            build_room_list_cache_key(self.owner.id, "friday", 2),
        )

    def test_redis_error_falls_back_to_database_payload(self):
        Room.objects.create(owner=self.owner, name="Fallback room", code="CACHE-2")
        self.client.force_login(self.owner)

        with patch("apps.majon.cache.cache.get", side_effect=RedisError("down")):
            response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["items"][0]["name"], "Fallback room")

    def test_create_and_delete_invalidate_cached_room_list_after_commit(self):
        self.client.force_login(self.owner)
        self.assertEqual(self.client.get(self.url).json()["total_count"], 0)

        with self.captureOnCommitCallbacks(execute=True):
            room = Room.objects.create(owner=self.owner, name="New room", code="CACHE-3")
        self.assertEqual(self.client.get(self.url).json()["total_count"], 1)

        with self.captureOnCommitCallbacks(execute=True):
            room.delete()
        self.assertEqual(self.client.get(self.url).json()["total_count"], 0)

    def test_owner_transfer_invalidates_both_cached_lists(self):
        room = Room.objects.create(owner=self.owner, name="Transfer room", code="CACHE-4")
        self.client.force_login(self.owner)
        self.client.get(self.url)
        self.client.force_login(self.other_owner)
        self.client.get(self.url)

        with self.captureOnCommitCallbacks(execute=True):
            room.owner = self.other_owner
            room.save()

        self.client.force_login(self.owner)
        self.assertEqual(self.client.get(self.url).json()["total_count"], 0)
        self.client.force_login(self.other_owner)
        self.assertEqual(self.client.get(self.url).json()["total_count"], 1)

    def test_rollback_does_not_advance_the_cache_version(self):
        from .cache import get_owner_version

        before = get_owner_version(self.owner.id)
        with transaction.atomic():
            Room.objects.create(owner=self.owner, name="Rolled back", code="CACHE-5")
            transaction.set_rollback(True)

        self.assertEqual(get_owner_version(self.owner.id), before)

    def test_redis_error_during_invalidation_does_not_block_room_creation(self):
        from .cache import get_owner_version

        get_owner_version(self.owner.id)
        with patch("apps.majon.cache.cache.incr", side_effect=RedisError("down")):
            with self.captureOnCommitCallbacks(execute=True):
                Room.objects.create(owner=self.owner, name="Still saved", code="CACHE-6")

        self.assertTrue(Room.objects.filter(code="CACHE-6").exists())
