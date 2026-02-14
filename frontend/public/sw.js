// JAN-SATHI OFFLINE-FIRST SERVICE WORKER
// Professional implementation for high-impact civic access in low-bandwidth areas.

const CACHE_NAME = 'jansathi-v2-offline';
const OFFLINE_URL = '/offline';

// Assets to cache for absolute offline accessibility
const STATIC_ASSETS = [
    '/',
    '/manifest.json',
    '/icons/icon-192x192.png',
    '/icons/icon-512x512.png',
    '/docs',
    '/chat'
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            console.log('[JanSathi SW] Pre-caching critical assets');
            return cache.addAll(STATIC_ASSETS);
        })
    );
    self.skipWaiting();
});

self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== CACHE_NAME) {
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
    self.clients.claim();
});

// Network-First strategy with Offline Fallback
self.addEventListener('fetch', (event) => {
    if (event.request.mode === 'navigate') {
        event.respondWith(
            fetch(event.request).catch(() => {
                return caches.match(event.request) || caches.match('/');
            })
        );
        return;
    }

    event.respondWith(
        caches.match(event.request).then((response) => {
            return response || fetch(event.request).then((networkResponse) => {
                // Cache successful GET requests for resources
                if (event.request.method === 'GET' && networkResponse.status === 200) {
                    const cacheCopy = networkResponse.clone();
                    caches.open(CACHE_NAME).then((cache) => {
                        cache.put(event.request, cacheCopy);
                    });
                }
                return networkResponse;
            });
        }).catch(() => {
            // Background sync logic or generic offline response could go here
        })
    );
});
