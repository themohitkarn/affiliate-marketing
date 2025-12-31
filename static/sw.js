self.addEventListener("install", e => {
  e.waitUntil(
    caches.open("daily-deals").then(cache => {
      return cache.addAll(["/"]);
    })
  );
});
