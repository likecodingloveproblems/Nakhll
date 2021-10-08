let CACHE_VERSION = 0.0;
let CURRENT_CACHE = {
    static: 'front-cache-v' + CACHE_VERSION,
    dynamc: 'dynamic-cache-v' + CACHE_VERSION,
};

self.addEventListener('install', function (evt) {
    self.skipWaiting();

    evt.waitUntil(
        caches.open(CURRENT_CACHE.static)
            .then(cache => {
                cache.addAll([
                    '/',
                ])
            })
    )
})

self.addEventListener('activate', function (evt) {
    let expectedCacheNames = Object.values(CURRENT_CACHE);
    evt.waitUntil(
        caches.keys()
            .then(cacheNames => {
                return Promise.all(
                    cacheNames.map(item => {
                        if (!expectedCacheNames.includes(item)) {
                            return caches.delete(item);
                        }
                    })
                )
            })
    )
})

self.addEventListener('fetch', function (evt) {
    return true;
})
