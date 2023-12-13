export enum AuthLevel {
	LOADING = 0,
	UNAUTHORIZED = 1,
	USER = 2,
	ADMIN = 3,
}

export enum BackendAuthLevel {
	UNAUTHORIZED = 1,
	USER = 2,
	ADMIN = 3,
}
export interface BackendUser {
	email: string;
	auth_level: BackendAuthLevel;
}

export interface BackendDecodedJWT {
	sub: string;
	auth_level: BackendAuthLevel;
	exp: number;
}
