import { getAccessToken } from "auth";
import axios from "axios";
import { setupCache } from "axios-cache-interceptor";
import { getBackendUrl } from "helpers";

// TODO: Add interceptor which refreshes token if it is expired
// See this: https://www.thedutchlab.com/en/insights/using-axios-interceptors-for-refreshing-your-api-token
export const apiFactory = () => {
	const instance = axios.create({
		baseURL: getBackendUrl(),
	});
	instance.interceptors.request.use(async (config) => {
		const token = await getAccessToken();
		config.headers.Authorization = `Bearer ${token}`;
		return config;
	});
	return setupCache(instance, { methods: ["get", "post"] });
};
