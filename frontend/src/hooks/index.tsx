import { getAuthLevel } from "auth";
import { AuthLevel } from "interfaces";
import { useEffect, useState } from "react";

export function useIsAuthorized() {
	const [authLevel, setAuthLevel] = useState(AuthLevel.LOADING);

	useEffect(() => {
		getAuthLevel().then((level) => setAuthLevel(level));
	}, []);

	return authLevel;
}
