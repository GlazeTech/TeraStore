import axios, { AxiosResponse } from "axios";
import { getBackendUrl } from "helpers";
import { BackendUser } from "interfaces";
import { clearAccessToken, setAccessToken } from "./accessToken";

const authService = axios.create({
	baseURL: getBackendUrl(),
});

// TODO: Add test
export async function login(username: string, password: string) {
	return authService
		.post(
			"/auth/login",
			{
				username: username,
				password: password,
			},
			{
				headers: {
					"Content-Type": "application/x-www-form-urlencoded",
				},
			},
		)
		.then((resp) => {
			setAccessToken(resp.data.accessToken);
			return resp.data.accessToken;
		});
}

export async function refreshAccessToken(): Promise<string> {
	return authService.get("/auth/refresh").then((resp) => {
		return resp.data.accessToken;
	});
}

export async function register(
	email: string,
	password: string,
): Promise<AxiosResponse> {
	return authService.post("/auth/signup", {
		email,
		password,
	});
}

// TODO: Add test
export async function logout(): Promise<void> {
	clearAccessToken();
	return authService.post("/auth/logout");
}

export async function getUsers(): Promise<BackendUser[]> {
	return authService.get("/auth/users").then((resp) => resp.data);
}

export async function updateUser(
	updatedUser: BackendUser,
): Promise<AxiosResponse> {
	return authService.post("/auth/update", updatedUser);
}

export async function deleteUser(user: BackendUser): Promise<AxiosResponse> {
	return authService.post("/auth/delete", user);
}
