import axios from "axios";

const api = axios.create({
	baseURL: "http://0.0.0.0:8000",
});

export async function pingBackend(): Promise<string> {
	return api.get("/").then((resp) => {
		return resp.data.message;
	});
}

// TODO: Add true http get
export async function getPulseKeys(): Promise<string[]> {
	return api.get("/").then(() => {
		return ["key1", "key2"];
	});
}

// TODO: Add true http get
export async function getKeyValues(key: string): Promise<string[]> {
	return api.get("/").then(() => {
		return [`${key}_val1`, `${key}_val2`, `${key}_val3`];
	});
}
