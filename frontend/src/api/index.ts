import axios from "axios";
import { PulseFilter } from "interfaces";
const api = axios.create({
	baseURL: "http://0.0.0.0:8000",
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
