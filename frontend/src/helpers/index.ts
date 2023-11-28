import { getFilteredPulses, getKeyValues } from "api";
import { FilterResult, PulseStringFilter, StringAttrKey } from "classes";
import { PulseFilter } from "interfaces";

export async function getFilterResultsForEachStringValue(
	key: StringAttrKey,
	pulseFilters: PulseFilter[],
): Promise<FilterResult[]> {
	const keyValues = await getKeyValues<string[]>(key);
	const allFilters = keyValues.map((attrValue) => [
		...pulseFilters,
		new PulseStringFilter(key, attrValue as string),
	]);
	return Promise.all(
		allFilters.map(async (filters) => getFilteredPulses(filters)),
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

export const sortPulseFilters = (filters: PulseFilter[]) => {
	// Sorts pulsefilters according to their hash
	return filters
		.map((filter) => {
			return { filter: filter, hash: filter.hash() };
		})
		.sort((a, b) => {
			if (a.hash > b.hash) {
				return 1;
			} else if (a.hash < b.hash) {
				return -1;
			} else {
				return 0;
			}
		})
		.map((obj) => obj.filter);
};

export function uniqueElements<T>(list: T[]): T[] {
	const uniqueSet = new Set(list);
	return [...uniqueSet];
}

export function getBackendUrl(): string {
	// import.meta.env.* is only available in production
	// for test runs, URL is injected via environment variables
	// Default to localhost:8000, when running in dev mode
	return import.meta.env.PROD
		? import.meta.env.VITE_BACKEND_URL
		: process.env.BACKEND_URL
		? `http://${process.env.BACKEND_URL}`
		: "http://0.0.0.0:8000";
}
