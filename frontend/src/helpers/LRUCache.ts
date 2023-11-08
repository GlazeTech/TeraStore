export class LRUCache<T> {
	private capacity: number;
	private cache: Map<string, T>;
	private accessOrder: string[] = [];

	constructor(capacity: number) {
		this.capacity = capacity;
		this.cache = new Map<string, T>();
	}

	get(key: string): T | undefined {
		if (this.cache.has(key)) {
			this.updateAccessOrder(key);
			return this.cache.get(key);
		} else {
			return undefined;
		}
	}

	set(key: string, value: T): void {
		if (this.cache.size >= this.capacity) {
			// Remove the least recently used key
			const lruKey = this.accessOrder.shift();
			if (lruKey) {
				this.cache.delete(lruKey);
			}
		}

		this.accessOrder.push(key);
		this.cache.set(key, value);
	}

	private updateAccessOrder(key: string) {
		// Move the accessed key to the end of the access order
		const index = this.accessOrder.indexOf(key);
		if (index !== -1) {
			this.accessOrder.splice(index, 1);
			this.accessOrder.push(key);
		}
	}
}
