import { getAuthLevel } from "auth";
import { useEffect, useState } from "react";
import { AuthLevel } from "interfaces";

export function useIsAuthorized() {
	const [authLevel, setAuthLevel] = useState(AuthLevel.LOADING);

	useEffect(() => {
		getAuthLevel().then((level) => setAuthLevel(level));
	}, []);

	return authLevel;
}
