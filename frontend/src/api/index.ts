import {
	AnnotatedPulse,
	FilterResult,
	PulseStringFilter,
	StringAttrKey,
	attrKeyFactory,
} from "classes";
import { sortPulseFilters } from "helpers";
import {
	BackendAttrKey,
	BackendPulse,
	IAttrKey,
	PulseFilter,
	PulseID,
} from "interfaces";
import { BackendTHzDevice } from "interfaces/backend";
import { apiFactory } from "./factory";

const api = apiFactory();

export async function getPulseKeys(): Promise<IAttrKey[]> {
	return api.get<BackendAttrKey[]>("/attrs/keys").then((resp) => {
		return resp.data.map((attrKey) =>
			attrKeyFactory(attrKey.name, attrKey.data_type),
		);
	});
}

export async function getKeyValues<T>(key: IAttrKey): Promise<T> {
	return api.get<T>(`/attrs/${key.name}/values`).then((resp) => {
		return resp.data;
	});
}

export async function getFilteredPulses(
	filters: PulseFilter[],
): Promise<FilterResult> {
	return api
		.post<[PulseID, Date][]>("/attrs/filter", {
			// Sort pulsefilters for improved caching
			kv_pairs: sortPulseFilters(filters).map((filter) =>
				filter.asBackendFilter(),
			),
			columns: ["pulse_id", "creation_time"],
		})
		.then((resp) => {
			return new FilterResult(
				filters,
				resp.data.map((el) => {
					return {
						pulseID: el[0],
						creationTime: new Date(el[1]),
					};
				}),
			);
		});
}

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

export async function getPulses(
	pulseIDs: PulseID[],
): Promise<AnnotatedPulse[]> {
	return (
		api
			// sort pulse IDs for improved caching
			.post<BackendPulse[]>("/pulses/get", [...pulseIDs].sort())
			.then((resp) => {
				return resp.data.map(AnnotatedPulse.fromBackendPulse);
			})
	);
}

export async function uploadPulses(pulses: AnnotatedPulse[]) {
	return api
		.post<PulseID[]>(
			"/pulses/create",
			pulses.map((pulse) => pulse.asBackendCompatible()),
		)
		.then((resp) => resp.data)
		.catch((err) => {
			console.log(err);
		});
}

export async function getDevices() {
	return api.get<BackendTHzDevice[]>("/devices").then((resp) => resp.data);
}

export async function addDevice(serialNumber: string) {
	return api.post("/devices", { serial_number: serialNumber });
}
