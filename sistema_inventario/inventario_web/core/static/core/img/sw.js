// Instalación del Service Worker
self.addEventListener('install', (event) => {
    console.log('Service Worker de Inv System instalado correctamente.');
    self.skipWaiting();
});

self.addEventListener('activate', (event) => {
    console.log('Service Worker activado.');
});

// Interceptar peticiones (modo online-first)
self.addEventListener('fetch', (event) => {
    event.respondWith(fetch(event.request));
});