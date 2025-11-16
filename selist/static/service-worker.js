const CACHE_VERSION = 'selist-v1';
const STATIC_CACHE = `${CACHE_VERSION}-static`;
const DYNAMIC_CACHE = `${CACHE_VERSION}-dynamic`;
const OFFLINE_URL = '/offline/';

const STATIC_FILES = [
  '/',
  '/about/',
  '/static/css/style.css',
  '/static/js/main.js',
  '/static/chat/css/chat_style.css',
  '/static/chat/css/modal.css',
  '/static/chat/js/chat.js',
  '/static/chat/js/emoji-renderer.js',
  '/static/users/css/forms.css',
  '/static/users/css/profile.css',
  OFFLINE_URL,
];

self.addEventListener('install', (event) => {
  console.log('[Service Worker] Installing...');
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) => {
      console.log('[Service Worker] Caching static files');
      return Promise.all(
        STATIC_FILES.map(async (url) => {
          const req = new Request(url, { cache: 'reload' });
          try {
            await cache.add(req);
          } catch (e) {
            console.error(`[Service Worker] Échec mise en cache: ${url}`, e);
          }
        })
      );
    }).catch((error) => {
      console.error('[Service Worker] Failed to cache static files:', error);
    })
  );
  self.skipWaiting();
});


self.addEventListener('activate', (event) => {
  console.log('[Service Worker] Activating...');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name.startsWith('selist-') && name !== STATIC_CACHE && name !== DYNAMIC_CACHE)
          .map((name) => {
            console.log('[Service Worker] Deleting old cache:', name);
            return caches.delete(name);
          })
      );
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  if (request.method !== 'GET') {
    return;
  }

  if (url.pathname.startsWith('/admin/') || url.pathname.startsWith('/__debug__/')) {
    return;
  }

  event.respondWith(
    networkFirstStrategy(request)
      .catch(() => {
        if (request.mode === 'navigate') {
          return caches.match(OFFLINE_URL).then((response) => {
            if (response) {
              return response;
            }
            return new Response(
              '<html><body><h1>You are offline</h1><p>Please check your internet connection and try again.</p></body></html>',
              { headers: { 'Content-Type': 'text/html' } }
            );
          });
        }
        return new Response('Offline', { status: 503, statusText: 'Service Unavailable' });
      })
  );
});

async function networkFirstStrategy(request) {
  const cache = await caches.open(DYNAMIC_CACHE);

  try {
    const networkResponse = await fetch(request);

    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }

    return networkResponse;
  } catch (error) {
    console.log('[Service Worker] Network failed, trying cache:', request.url);
    const cachedResponse = await cache.match(request);

    if (cachedResponse) {
      return cachedResponse;
    }

    const staticCache = await caches.open(STATIC_CACHE);
    const staticResponse = await staticCache.match(request);

    if (staticResponse) {
      return staticResponse;
    }

    throw error;
  }
}

// Listen for messages from clients
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  if (event.data && event.data.type === 'CLEAR_CACHE') {
    event.waitUntil(
      (async () => {
        const cacheNames = await caches.keys();
        await Promise.all(
          cacheNames
            .filter((name) => name.startsWith('selist-'))
            .map((name) => caches.delete(name))
        );

        const staticCache = await caches.open(STATIC_CACHE);
        await staticCache.addAll(STATIC_FILES.map(url => new Request(url, { cache: 'reload' })));
      })()
    );
  }
});
