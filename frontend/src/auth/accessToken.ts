import { AuthLevel, BackendDecodedJWT } from "interfaces";
import { jwtDecode } from "jwt-decode";
import { refreshAccessToken } from "./auth-service";

// Use a global variable to store a JWT token used for authentication.
let accessToken: string | null = null;

export const getAccessToken = async () => {
	// If we already have an access token, we return it immediately.
	if (accessToken) {
		return accessToken;
	}

	// If page is refreshed (access token is lost), try to refresh access token.
	return refreshAccessToken()
		.then((token) => {
			setAccessToken(token);
			return token;
		})
		.catch(() => {
			return accessToken;
		});
};

export const setAccessToken = (token: string) => {
	accessToken = token;
};

export const clearAccessToken = () => {
	accessToken = null;
};

export const getAuthLevel = async () => {
	return getAccessToken().then((token) => {
		if (!token) {
			return AuthLevel.UNAUTHORIZED;
		}
		const decoded = jwtDecode(token) as BackendDecodedJWT;
		return decoded.auth_level as unknown as AuthLevel;
	});
};
