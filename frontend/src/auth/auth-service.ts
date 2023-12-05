import axios from "axios";
import { getBackendUrl } from "helpers";
import { clearAccessToken } from "./accessToken";

const authService = axios.create({
	baseURL: getBackendUrl(),
});

// export async function login(username: string, password: string) {
// 	return authService
// 		.post("/auth/login", {
// 			email,
// 			password,
// 		})
// 		.then((resp) => {
// 			setAccessToken(resp.data.accessToken);
// 			return resp.data.accessToken;
// 		});
// }

export async function login(_: string, __: string): Promise<string> {
	return new Promise((resolve) => {
		setTimeout(() => {
			resolve("fake-access-token");
		}, 1000);
	});
}

export async function refreshAccessToken(): Promise<string> {
	return authService.get("/auth/refresh").then((resp) => {
		return resp.data.accessToken;
	});
}

// export function register(email: string, password: string): Promise<void> {
// 	return authService.post("/auth/register", {
// 		email,
// 		password,
// 	});
// }

export function register(_: string, __: string): Promise<void> {
	return new Promise((resolve) => {
		setTimeout(() => {
			resolve();
		}, 1000);
	});
}

// export async function logout(): Promise<void> {
// 	clearAccessToken();
// 	return authService.post("/auth/logout");
// }

export async function logout(): Promise<void> {
	clearAccessToken();
	return new Promise((resolve) => {
		setTimeout(() => {
			resolve();
		}, 100);
	});
}
