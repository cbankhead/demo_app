from .models import PrefixDataCache

# How long saved data stays fresh: 24 hours.
CACHE_LIFETIME_SECONDS = 24 * 60 * 60

# Third-party IP-range endpoints (esp. Azure's) are slow/unreliable; cache
# results so repeated requests/imports don't re-fetch (or re-timeout) every time.
def get_or_fetch(cache_key, fetch_data):
    """Return saved data, or fetch it and save it for 24 hours.

    cache_key: Name used to find this saved data.
    fetch_data: Function that gets fresh data from a provider.
    """
    # Data already saved for this key, if it is still fresh.
    cached_data = PrefixDataCache.get_cached_data(cache_key)
    if cached_data is not None:
        return cached_data

    # New data returned by the provider.
    fresh_data = fetch_data()
    if fresh_data is None:
        return None

    PrefixDataCache.set_cached_data(cache_key, fresh_data, CACHE_LIFETIME_SECONDS)
    return fresh_data
