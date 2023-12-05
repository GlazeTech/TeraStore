import { LoadingOverlay } from "@mantine/core";
import App from "components/App";
import { AuthLevel, useIsAuthorized } from "hooks";
import { Navigate, useLocation } from "react-router-dom";

export default function Home() {
	const authLevel = useIsAuthorized();
	const location = useLocation();

	if (authLevel === AuthLevel.LOADING) {
		return <LoadingOverlay visible />;
	} else if (authLevel === AuthLevel.UNAUTHORIZED) {
		return <Navigate to="/login" state={{ from: location }} replace />;
	} else if (authLevel >= AuthLevel.USER) {
		return <App />;
	}
}
