import { Button, Group } from "@mantine/core";
import { logout } from "auth";
import { useState } from "react";
import { Navigate } from "react-router-dom";
import { useLocation } from "react-router-dom";

enum LoginStatus {
	LoggedIn = 1,
	LoggedOut = 2,
}

export default function Header() {
	const [loginStatus, setLoginStatus] = useState(LoginStatus.LoggedIn);
	const location = useLocation();

	const handleLogout = () => {
		logout().then(() => {
			setLoginStatus(LoginStatus.LoggedOut);
		});
	};

	if (loginStatus === LoginStatus.LoggedIn) {
		return (
			<Group justify="right">
				<Button mt={7} variant="subtle" onClick={handleLogout}>
					Log out
				</Button>
			</Group>
		);
	} else if (loginStatus === LoginStatus.LoggedOut) {
		return <Navigate to={"/login"} state={{ from: location }} replace />;
	}
}
