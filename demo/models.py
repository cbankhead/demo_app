from django.db import models
from django.utils import timezone
from datetime import timedelta

# Create your models here.


class PrefixDataCache(models.Model):
    cache_key = models.CharField(max_length=255, unique=True)
    payload = models.JSONField()
    expires_at = models.DateTimeField()

    @classmethod
    def get_cached_data(cls, cache_key):
        """Return saved data if it has not expired.

        cache_key: Name used to find the saved data.
        """
        try:
            # The saved row that matches this cache key.
            cache_item = cls.objects.get(cache_key=cache_key)
        except cls.DoesNotExist:
            return None

        # Delete old data instead of returning it.
        if cache_item.expires_at <= timezone.now():
            cache_item.delete()
            return None

        return cache_item.payload

    @classmethod
    def set_cached_data(cls, cache_key, payload, lifetime_seconds=3600):
        """Save data until its lifetime has passed.

        cache_key: Name used to find the saved data.
        payload: JSON data to save.
        lifetime_seconds: How long to keep the data, in seconds.
        """
        # The time when this saved data will expire.
        expires_at = timezone.now() + timedelta(seconds=lifetime_seconds)
        cls.objects.update_or_create(
            cache_key=cache_key,
            defaults={'payload': payload, 'expires_at': expires_at},
        )