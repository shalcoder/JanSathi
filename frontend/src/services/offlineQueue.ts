/**
 * Offline Action Queue – uses localStorage as a lightweight fallback
 * (no external deps). For production with idb, swap the storage layer below.
 *
 * Actions are queued when the device is offline and automatically flushed
 * when connectivity is restored.
 */

export type QueuedActionType = 'apply' | 'upload';

export interface QueuedAction {
    id: string;
    type: QueuedActionType;
    payload: Record<string, unknown>;
    createdAt: string;
    retries: number;
}

const QUEUE_KEY = 'jansathi_offline_queue';

// ─── Storage helpers ──────────────────────────────────────────────────────────

function readQueue(): QueuedAction[] {
    if (typeof window === 'undefined') return [];
    try {
        return JSON.parse(localStorage.getItem(QUEUE_KEY) || '[]');
    } catch {
        return [];
    }
}

function writeQueue(queue: QueuedAction[]): void {
    if (typeof window === 'undefined') return;
    localStorage.setItem(QUEUE_KEY, JSON.stringify(queue));
}

// ─── Public API ───────────────────────────────────────────────────────────────

/**
 * Add an action to the offline queue.
 */
export function enqueue(type: QueuedActionType, payload: Record<string, unknown>): QueuedAction {
    const action: QueuedAction = {
        id: `${type}-${Date.now()}-${Math.random().toString(36).slice(2)}`,
        type,
        payload,
        createdAt: new Date().toISOString(),
        retries: 0,
    };
    const queue = readQueue();
    queue.push(action);
    writeQueue(queue);
    return action;
}

/**
 * Remove a successfully processed action from the queue.
 */
export function dequeue(id: string): void {
    const queue = readQueue().filter(a => a.id !== id);
    writeQueue(queue);
}

/**
 * Read all queued actions.
 */
export function getQueue(): QueuedAction[] {
    return readQueue();
}

/**
 * Flush the queue. For each action, call `handler(action)`.
 * Successful actions are removed; failed ones have their retry count incremented.
 * Actions with retries >= maxRetries are dropped.
 */
export async function flushQueue(
    handler: (action: QueuedAction) => Promise<void>,
    maxRetries = 3
): Promise<{ succeeded: number; failed: number; dropped: number }> {
    const queue = readQueue();
    if (queue.length === 0) return { succeeded: 0, failed: 0, dropped: 0 };

    let succeeded = 0;
    let failed = 0;
    let dropped = 0;

    for (const action of queue) {
        try {
            await handler(action);
            dequeue(action.id);
            succeeded++;
        } catch (err) {
            console.error(`[offlineQueue] Action ${action.id} failed:`, err);
            if (action.retries >= maxRetries) {
                dequeue(action.id);
                dropped++;
            } else {
                const updated = readQueue().map(a =>
                    a.id === action.id ? { ...a, retries: a.retries + 1 } : a
                );
                writeQueue(updated);
                failed++;
            }
        }
    }

    return { succeeded, failed, dropped };
}

/**
 * Register a global online listener that triggers a flush.
 * Call this once at app startup.
 */
export function registerOnlineFlush(
    handler: (action: QueuedAction) => Promise<void>
): () => void {
    if (typeof window === 'undefined') return () => {};
    const onOnline = () => {
        flushQueue(handler).then(result => {
            if (result.succeeded > 0 || result.dropped > 0) {
                console.log('[offlineQueue] Flush result:', result);
            }
        });
    };
    window.addEventListener('online', onOnline);
    return () => window.removeEventListener('online', onOnline);
}
