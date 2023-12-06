import axios from "axios";
import { setupCache } from "axios-cache-interceptor";
import { AnnotatedPulse, FilterResult, attrKeyFactory } from "classes";
import { getBackendUrl, sortPulseFilters } from "helpers";
import {
	BackendAttrKey,
	BackendPulse,
	IAttrKey,
	PulseFilter,
	PulseID,
} from "interfaces";
import { BackendTHzDevice } from "interfaces/backend";

const api = setupCache(
	axios.create({
		baseURL: getBackendUrl(),
	}),
	{ methods: ["get", "post"] },
);

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
