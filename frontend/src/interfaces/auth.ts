export enum AuthLevel {
	LOADING = 1,
	UNAUTHORIZED = 2,
	USER = 3,
	ADMIN = 4,
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
