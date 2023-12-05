import { getAuthLevel } from "auth";
import { useEffect, useState } from "react";

export enum AuthLevel {
	LOADING = 1,
	UNAUTHORIZED = 2,
	USER = 3,
	ADMIN = 4,
}

export function useIsAuthorized() {
	const [authLevel, setAuthLevel] = useState(AuthLevel.LOADING);

	useEffect(() => {
		getAuthLevel().then((level) => setAuthLevel(level));
	}, []);

	return authLevel;
}
