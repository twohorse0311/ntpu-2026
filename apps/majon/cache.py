import hashlib
import logging

from django.core.cache import cache
from redis.exceptions import RedisError


logger = logging.getLogger(__name__)


def _version_key(owner_id):
    return f"room-list:version:owner:{owner_id}"


def _query_hash(query):
    return hashlib.sha256(query.encode()).hexdigest()


def build_room_list_cache_key(owner_id, query, page, version=1):
    return (
        f"room-list:data:v{version}:owner:{owner_id}:query:{_query_hash(query)}:page:{page}"
    )


def get_owner_version(owner_id):
    try:
        version_key = _version_key(owner_id)
        version = cache.get(version_key)
        if version is None:
            cache.add(version_key, 1, timeout=None)
            version = cache.get(version_key) or 1
        return version
    except RedisError:
        logger.warning("Room-list cache version lookup failed", exc_info=True)
        return None


def get_cached_room_list(owner_id, query, page):
    version = get_owner_version(owner_id)
    if version is None:
        return None
    try:
        return cache.get(build_room_list_cache_key(owner_id, query, page, version))
    except RedisError:
        logger.warning("Room-list cache read failed", exc_info=True)
        return None


def cache_room_list(owner_id, query, page, payload):
    version = get_owner_version(owner_id)
    if version is None:
        return
    try:
        cache.set(build_room_list_cache_key(owner_id, query, page, version), payload)
    except RedisError:
        logger.warning("Room-list cache write failed", exc_info=True)


def invalidate_room_list(owner_id):
    try:
        version_key = _version_key(owner_id)
        if cache.get(version_key) is None:
            cache.add(version_key, 1, timeout=None)
        cache.incr(version_key)
    except RedisError:
        logger.warning("Room-list cache invalidation failed", exc_info=True)
