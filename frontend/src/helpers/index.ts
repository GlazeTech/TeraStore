import { PulseFilter } from "interfaces";

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
	try {
		if (import.meta.env.PROD) {
			return import.meta.env.VITE_BACKEND_URL;
		}
	} catch (e) {}

	// for test runs, URL is injected via environment variables - this won't be available in a browser
	try {
		if (process.env.BACKEND_URL) {
			return `http://${process.env.BACKEND_URL}`;
		}
	} catch (e) {}

	// Default to localhost:8000, when running in dev mode
	return "http://0.0.0.0:8000";
}

export const getEnumKeys = (enumObj: object): string[] => {
	return Object.keys(enumObj).filter(
		(x) => !(parseInt(x) >= 0),
	) as (keyof typeof enumObj)[];
};
