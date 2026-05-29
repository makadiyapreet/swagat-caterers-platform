/**
 * Section 24: IndexedDB Offline Sync Module
 * Stores menu items, events, and failed form submissions locally.
 */

const DB_NAME = 'swagat_offline';
const DB_VERSION = 1;

// Open IndexedDB
function openDB() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open(DB_NAME, DB_VERSION);
        
        request.onupgradeneeded = (event) => {
            const db = event.target.result;
            
            // Store for menu items
            if (!db.objectStoreNames.contains('menu_items')) {
                db.createObjectStore('menu_items', { keyPath: 'id' });
            }
            
            // Store for events
            if (!db.objectStoreNames.contains('events')) {
                db.createObjectStore('events', { keyPath: 'id' });
            }
            
            // Store for pending form submissions
            if (!db.objectStoreNames.contains('sync_queue')) {
                db.createObjectStore('sync_queue', { keyPath: 'id', autoIncrement: true });
            }
        };
        
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
    });
}

// Cache menu items from API
async function cacheMenuItems() {
    try {
        const resp = await fetch('/api/menu/items/');
        if (!resp.ok) return;
        const items = await resp.json();
        
        const db = await openDB();
        const tx = db.transaction('menu_items', 'readwrite');
        const store = tx.objectStore('menu_items');
        
        // Clear old data
        store.clear();
        items.forEach(item => store.put(item));
        
        console.log(`[Offline] Cached ${items.length} menu items`);
    } catch (e) {
        console.log('[Offline] Menu cache skipped (offline)');
    }
}

// Cache events from API
async function cacheEvents() {
    try {
        const resp = await fetch('/api/events/list/');
        if (!resp.ok) return;
        const events = await resp.json();
        
        const db = await openDB();
        const tx = db.transaction('events', 'readwrite');
        const store = tx.objectStore('events');
        
        store.clear();
        events.forEach(event => store.put(event));
        
        console.log(`[Offline] Cached ${events.length} events`);
    } catch (e) {
        console.log('[Offline] Events cache skipped (offline)');
    }
}

// Get cached data
async function getCachedData(storeName) {
    const db = await openDB();
    return new Promise((resolve, reject) => {
        const tx = db.transaction(storeName, 'readonly');
        const store = tx.objectStore(storeName);
        const request = store.getAll();
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
    });
}

// Queue failed POST for later sync
async function queueForSync(url, method, data) {
    const db = await openDB();
    const tx = db.transaction('sync_queue', 'readwrite');
    const store = tx.objectStore('sync_queue');
    store.add({
        url: url,
        method: method,
        data: data,
        timestamp: new Date().toISOString(),
    });
    console.log('[Offline] Queued request for sync:', url);
}

// Process sync queue when back online
async function processSyncQueue() {
    const db = await openDB();
    const tx = db.transaction('sync_queue', 'readwrite');
    const store = tx.objectStore('sync_queue');
    const request = store.getAll();
    
    request.onsuccess = async () => {
        const queue = request.result;
        if (queue.length === 0) return;
        
        console.log(`[Offline] Processing ${queue.length} queued requests...`);
        
        for (const item of queue) {
            try {
                await fetch(item.url, {
                    method: item.method,
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(item.data),
                });
                // Remove from queue on success
                const deleteTx = db.transaction('sync_queue', 'readwrite');
                deleteTx.objectStore('sync_queue').delete(item.id);
                console.log(`[Offline] Synced: ${item.url}`);
            } catch (e) {
                console.log(`[Offline] Still failing: ${item.url}`);
            }
        }
    };
}

// Offline detection + banner
function setupOfflineDetection() {
    const banner = document.createElement('div');
    banner.id = 'offline-banner';
    banner.innerHTML = '📡 You are offline. Some features may be limited.';
    banner.style.cssText = `
        position: fixed; top: 0; left: 0; right: 0; z-index: 99999;
        background: linear-gradient(135deg, #c0392b, #e74c3c);
        color: white; text-align: center; padding: 10px;
        font-weight: 600; font-size: 0.85rem;
        display: none; transition: transform 0.3s;
    `;
    document.body.prepend(banner);

    window.addEventListener('offline', () => {
        banner.style.display = 'block';
    });

    window.addEventListener('online', () => {
        banner.style.display = 'none';
        processSyncQueue();
    });

    if (!navigator.onLine) {
        banner.style.display = 'block';
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    setupOfflineDetection();
    
    // Cache data when online
    if (navigator.onLine) {
        cacheMenuItems();
        cacheEvents();
    }
});

// Listen for SW sync complete message
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.addEventListener('message', (event) => {
        if (event.data && event.data.type === 'SYNC_COMPLETE') {
            console.log('[Offline] Background sync completed');
            processSyncQueue();
        }
    });
}
