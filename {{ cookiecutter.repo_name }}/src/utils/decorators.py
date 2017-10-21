import functools
import os
import pickle


cache_listing_file = '.cache_listing'
if os.path.exists(cache_listing_file):
    with open(cache_listing_file, 'rb') as f:
        cache_listing = pickle.load(f)
else:
    cache_listing = {}


def cache(cache_dir):
    def _cache(f):
        @functools.wraps(f)
        def decorated(*args, cache_id=None, **kwargs):
            if cache_id is None:
                return f(*args, **kwargs)

            if f.__name__ not in cache_listing:
                cache_listing[f.__name__] = set()

            cache_file = os.path.abspath(os.path.join(
                cache_dir, '{}-{}.pkl'.format(f.__name__, cache_id)))

            # cache hit
            if os.path.exists(cache_file):
                with open(cache_file, 'rb') as infile:
                    result = pickle.load(infile)

            # cache miss
            else:
                result = f(*args, **kwargs)
                with open(cache_file, 'wb') as outfile:
                    pickle.dump(result, outfile)

            cache_listing[f.__name__].add(cache_file)
            with open(cache_listing_file, 'wb') as outfile:
                pickle.dump(cache_listing, outfile)
            return result

        
        def clear_cache_files(func):
            cache_files = cache_listing.get(func.__name__, [])
            for cache_file in cache_files:
                os.remove(cache_file)
            del cache_listing[func.__name__]

        
        def cache_files(func):
            return cache_listing.get(func.__name__, [])


        decorated.clear_cache_files = functools.partial(clear_cache_files, f)
        decorated.cache_files = functools.partial(cache_files, f)
        return decorated
    return _cache
