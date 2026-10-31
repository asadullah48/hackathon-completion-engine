/// <reference lib="webworker" />

// Define the cache name and static assets
const CACHE_NAME = 'h3-todo-v1';
const STATIC_CACHE = 'static-v1';
const DATA_CACHE = 'data-v1';

// Assets to cache statically
const STATIC_ASSETS = [
  '/',
  '/manifest.json',
  '/favicon.ico',
  '/icons/icon-192x192.png',
  '/icons/icon-512x512.png',
  '/_next/static/css/app.css',
  // Add other static assets as needed
];

// Install event - cache static assets
self.addEventListener('install', (event: ExtendableEvent) => {
  console.log('[Service Worker] Installing...');
  
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then((cache) => {
        console.log('[Service Worker] Pre-caching static assets');
        return cache.addAll(STATIC_ASSETS);
      })
      .then(() => {
        console.log('[Service Worker] Installation complete');
        return self.skipWaiting(); // Force the waiting service worker to become the active one
      })
      .catch((error) => {
        console.error('[Service Worker] Installation failed:', error);
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event: ExtendableEvent) => {
  console.log('[Service Worker] Activating...');
  
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== STATIC_CACHE && cacheName !== DATA_CACHE) {
            console.log('[Service Worker] Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
          return Promise.resolve();
        })
      );
    })
    .then(() => {
      console.log('[Service Worker] Activation complete');
      return self.clients.claim(); // Take control of all clients immediately
    })
  );
});

// Fetch event - handle requests
self.addEventListener('fetch', (event: FetchEvent) => {
  // Skip non-GET requests
  if (event.request.method !== 'GET') {
    return;
  }

  // Handle API requests separately
  if (event.request.url.includes('/api/')) {
    event.respondWith(handleApiRequest(event.request));
    return;
  }

  // Handle static assets
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        // Return cached version if available
        if (response) {
          console.log('[Service Worker] Serving from cache:', event.request.url);
          return response;
        }

        // Otherwise fetch from network
        return fetch(event.request)
          .then((networkResponse) => {
            // Cache the response for future requests
            if (networkResponse.status === 200) {
              const responseClone = networkResponse.clone();
              caches.open(DATA_CACHE)
                .then((cache) => {
                  cache.put(event.request, responseClone);
                });
            }
            return networkResponse;
          })
          .catch(() => {
            // If network fails, try to serve from cache
            return caches.match('/offline.html')
              .then((offlineResponse) => {
                return offlineResponse || new Response('Offline', {
                  status: 200,
                  headers: { 'Content-Type': 'text/html' }
                });
              });
          });
      })
  );
});

// Function to handle API requests with cache strategy
async function handleApiRequest(request: Request): Promise<Response> {
  const cache = await caches.open(DATA_CACHE);
  const cachedResponse = await cache.match(request);

  // Try network first
  try {
    const networkResponse = await fetch(request);
    
    // If successful, update cache
    if (networkResponse.status === 200) {
      const responseClone = networkResponse.clone();
      cache.put(request, responseClone);
    }
    
    return networkResponse;
  } catch (error) {
    // If network fails, return cached response
    if (cachedResponse) {
      console.log('[Service Worker] Serving API from cache:', request.url);
      return cachedResponse;
    }
    
    // If no cache available, return error response
    return new Response(JSON.stringify({ error: 'Network error, offline mode' }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

// Listen for messages from the client
self.addEventListener('message', (event: ExtendableMessageEvent) => {
  console.log('[Service Worker] Received message from client:', event.data);
  
  // Handle specific message types
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  
  // Handle cache refresh
  if (event.data && event.data.type === 'REFRESH_CACHE') {
    // Clear data cache to force fresh data on next request
    caches.delete(DATA_CACHE);
  }
});