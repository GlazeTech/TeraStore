import { Button, Group } from "@mantine/core";
import { logout } from "auth";
import { useIsAuthorized } from "hooks";
import { AuthLevel } from "interfaces";
import { useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";

enum LoginStatus {
	LoggedIn = 1,
	LoggedOut = 2,
}

export default function Header() {
	const [loginStatus, setLoginStatus] = useState(LoginStatus.LoggedIn);
	const authLevel = useIsAuthorized();
	const navigate = useNavigate();

	const handleLogout = () => {
		logout().then(() => {
			setLoginStatus(LoginStatus.LoggedOut);
		});
	};

	if (loginStatus === LoginStatus.LoggedIn) {
		return (
			<Group justify="space-between">
				{authLevel === AuthLevel.ADMIN && (
					<Group justify="left">
						<Button mt={7} variant="subtle" onClick={() => navigate("/")}>
							Home
						</Button>

						<Button mt={7} variant="subtle" onClick={() => navigate("/admin")}>
							Dashboard
						</Button>
					</Group>
				)}
				<Group justify="right">
					<Button mt={7} variant="subtle" onClick={handleLogout}>
						Log out
					</Button>
				</Group>
			</Group>
		);
	} else if (loginStatus === LoginStatus.LoggedOut) {
		return <Navigate to={"/login"} />;
	}
}
