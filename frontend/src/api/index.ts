import axios from "axios";
import { Pulse } from "classes";
import { cacheFunction } from "helpers";
import { PulseFilter, PulseFromBackend } from "interfaces";

const api = axios.create({
	baseURL: import.meta.env.PROD
		? import.meta.env.VITE_BACKEND_URL
		: "http://0.0.0.0:8000",
});

export async function pingBackend(): Promise<string> {
	return api.get("/").then((resp) => {
		return resp.data.message;
	});
}

export async function getPulseKeys(): Promise<string[]> {
	return api.get("/attrs/keys").then((resp) => {
		return resp.data;
	});
}

export async function getKeyValues(key: string): Promise<string[]> {
	return api.get(`/attrs/${key}/values`).then((resp) => {
		return resp.data;
	});
}

export async function getFilteredPulses(
	filters: PulseFilter[],
): Promise<string[]> {
	return api.post("/attrs/filter", filters).then((resp) => {
		return resp.data;
	});
}

export async function getPulse(pulseID: string): Promise<Pulse> {
	return api.get(`/pulses/${pulseID}`).then((resp) => {
		return new Pulse(
			resp.data.delays,
			resp.data.signal,
			resp.data.integration_time,
			new Date(resp.data.creation_time),
			resp.data.pulse_id,
		);
	});
}

export async function getPulses(pulseIDs: string[]): Promise<Pulse[]> {
	return api.post("/pulses/get", pulseIDs).then((resp) => {
		return resp.data.map(
			(el: PulseFromBackend) =>
				new Pulse(
					el.delays,
					el.signal,
					el.integration_time,
					new Date(el.creation_time),
					el.pulse_id,
				),
		);
	});
}

export const cachedGetKeyValues = cacheFunction(
	getKeyValues,
	100,
	(arg) => arg,
);

export const cachedGetFilteredPulses = cacheFunction(
	getFilteredPulses,
	50,
	(arg) =>
		[...arg]
			.sort((a, b) => a.key.localeCompare(b.key))
			.map((filter) => `${filter.key}:${filter.value}`)
			.join(","),
);

export const cachedGetPulse = cacheFunction(getPulse, 100, (arg) => arg);

export const cachedGetPulses = cacheFunction(getPulses, 15, (arg) =>
	[...arg].sort((a, b) => a.localeCompare(b)).join(","),
);
