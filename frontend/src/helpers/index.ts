import { cachedGetFilteredPulses, cachedGetKeyValues } from "api";
import { FilterResult } from "classes";
import { PulseFilter } from "interfaces";
import { LRUCache } from "./LRUCache";

export async function getFilterResultsForEachKeyValue(
	key: string,
	pulseFilters: PulseFilter[],
): Promise<FilterResult[]> {
	const keyValues = await cachedGetKeyValues(key);
	const newFilters = keyValues.map((value) => [
		...pulseFilters,
		{ key: key, value: value },
	]);
	const pulsesPerFilter = await Promise.all(
		newFilters.map(async (filter) => cachedGetFilteredPulses(filter)),
	);
	return pulsesPerFilter.map(
		(pulseArr, idx) => new FilterResult(newFilters[idx], pulseArr),
	);
}

export function downloadJson(jsonData: object, fileName: string): undefined {
	const jsonString = JSON.stringify(jsonData, null, 2); // The second argument specifies the number of spaces for formatting

	// Convert to a blob and make a temporary anchor element to trigger the download
	const blob = new Blob([jsonString], { type: "application/json" });
	const url = URL.createObjectURL(blob);
	const a = document.createElement("a");
	a.href = url;
	a.download = fileName;
	a.click();

	// Clean up the URL and the anchor element
	URL.revokeObjectURL(url);
}

export function cacheFunction<T, U>(
	func: (args: U) => Promise<T>,
	capacity: number,
	hashFunction: (arg: U) => string,
) {
	const cache = new LRUCache<T>(capacity);

	return async function (args: U): Promise<T> {
		const cacheKey = hashFunction(args);

		let result = cache.get(cacheKey);

		if (result) {
			return result;
		} else {
			result = await func(args);
			cache.set(cacheKey, result);
			return result;
		}
	};
}
