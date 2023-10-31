import { getFilteredPulses, getKeyValues } from "api";
import { FilterResult } from "classes";
import { PulseFilter } from "interfaces";

export async function getFilterResultsForEachKeyValue(
	key: string,
	pulseFilters: PulseFilter[],
): Promise<FilterResult[]> {
	const keyValues = await getKeyValues(key);
	const newFilters = keyValues.map((value) => [
		...pulseFilters,
		{ key: key, value: value },
	]);
	const pulsesPerFilter = await Promise.all(
		newFilters.map(async (filter) => getFilteredPulses(filter)),
	);
	return pulsesPerFilter.map(
		(pulseArr, idx) => new FilterResult(newFilters[idx], pulseArr),
	);
}
