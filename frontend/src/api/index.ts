import axios from "axios";
import { setupCache } from "axios-cache-interceptor";
import { AnnotatedPulse, FilterResult, Pulse, attrKeyFactory } from "classes";
import { sortPulseFilters } from "helpers";
import {
	BackendAttrKey,
	BackendPulse,
	IAttrKey,
	PulseFilter,
	PulseID,
} from "interfaces";
import { BackendTHzDevice } from "interfaces/backend";

// Potential TODO: Reset cache when pulses are uploaded - see this https://axios-cache-interceptor.js.org/guide/invalidating-cache
const api = setupCache(
	axios.create({
		baseURL: import.meta.env.PROD
			? import.meta.env.VITE_BACKEND_URL
			: "http://0.0.0.0:8000",
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
		.post<PulseID[]>(
			"/attrs/filter",
			// Sort pulsefilters for improved caching
			sortPulseFilters(filters).map((filter) => filter.asBackendFilter()),
		)
		.then((resp) => {
			return new FilterResult(filters, resp.data);
		});
}

export async function getPulse(pulseID: PulseID): Promise<Pulse> {
	return api.get<BackendPulse>(`/pulses/${pulseID}`).then((resp) => {
		return new Pulse(
			resp.data.delays,
			resp.data.signal,
			resp.data.integration_time,
			new Date(resp.data.creation_time),
			resp.data.pulse_id,
		);
	});
}

export async function getPulses(pulseIDs: PulseID[]): Promise<Pulse[]> {
	return (
		api
			// sort pulse IDs for improved caching
			.post<BackendPulse[]>("/pulses/get", [...pulseIDs].sort())
			.then((resp) => {
				return resp.data.map(
					(el: BackendPulse) =>
						new Pulse(
							el.delays,
							el.signal,
							el.integration_time,
							new Date(el.creation_time),
							el.pulse_id,
						),
				);
			})
	);
}

// TODO: Implement uploadPulses
export async function uploadPulses(pulses: AnnotatedPulse[]) {
	return new Promise<void>((resolve) => {
		setTimeout(() => {
			resolve();
		}, 1000);
	});
}

export async function getDevices() {
	return api.get<BackendTHzDevice[]>("/devices").then((resp) => resp.data);
}
