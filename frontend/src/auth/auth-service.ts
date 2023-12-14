import axios, { AxiosResponse } from "axios";
import { getBackendUrl } from "helpers";
import { BackendUser } from "interfaces";
import {
	clearAccessToken,
	setAccessToken,
	getAccessToken,
} from "./accessToken";

const authService = axios.create({
	baseURL: getBackendUrl(),
});

const getCredentials = async () => {
	const token = await getAccessToken();
	return {
		headers: {
			Authorization: `Bearer ${token}`,
		},
		withCredentials: true,
	};
};

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
				withCredentials: true,
			},
		)
		.then((resp) => {
			setAccessToken(resp.data.access_token);
			return resp.data.access_token;
		});
}

export async function refreshAccessToken(): Promise<string> {
	return authService
		.get("/auth/refresh", {
			withCredentials: true,
		})
		.then((resp) => {
			return resp.data.access_token;
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
	const accessToken = await getAccessToken();
	clearAccessToken();
	return authService.get("/user/logout", {
		headers: { Authorization: `Bearer ${accessToken}` },
		withCredentials: true,
	});
}

export async function getUsers(): Promise<BackendUser[]> {
	return authService
		.get("/user/users", await getCredentials())
		.then((resp) => resp.data);
}

export async function updateUser(
	updatedUser: BackendUser,
): Promise<AxiosResponse> {
	return authService.post("/user/update", updatedUser, await getCredentials());
}

export async function deleteUser(user: BackendUser): Promise<AxiosResponse> {
	return authService.post("/user/delete", user, await getCredentials());
}
