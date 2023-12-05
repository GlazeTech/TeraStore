import { LoadingOverlay } from "@mantine/core";
import AdminDashboard from "components/AdminDashboard";
import { AuthLevel, useIsAuthorized } from "hooks";
import { Navigate, useLocation } from "react-router-dom";

export default function Admin() {
	const authLevel = useIsAuthorized();
	const location = useLocation();

	if (authLevel === AuthLevel.LOADING) {
		return <LoadingOverlay visible />;
	} else if (authLevel === AuthLevel.UNAUTHORIZED) {
		return <Navigate to="/login" state={{ from: location }} replace />;
	} else if (authLevel === AuthLevel.USER) {
		return <Navigate to="/" state={{ from: location }} replace />;
	} else if (authLevel === AuthLevel.ADMIN) {
		return <AdminDashboard />;
	}
}
