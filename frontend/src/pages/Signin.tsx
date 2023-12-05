import {
	Box,
	Button,
	Card,
	LoadingOverlay,
	Stack,
	TextInput,
} from "@mantine/core";
import { notifications } from "@mantine/notifications";
import { login, setAccessToken } from "auth";
import { FormEvent, useState } from "react";
import { Link, Navigate, useLocation } from "react-router-dom";

enum SigninStatus {
	NOT_LOGGED_IN = 1,
	LOGGING_IN = 2,
	LOGGED_IN = 3,
}

const style = {
	alignItems: "center",
};

export default function Signin() {
	const [username, setUsername] = useState("");
	const [password, setPassword] = useState("");
	const location = useLocation();

	const [signinStatus, setSigninStatus] = useState(SigninStatus.NOT_LOGGED_IN);

	const handleLogin = (event: FormEvent<HTMLFormElement>) => {
		event.preventDefault();
		setSigninStatus(SigninStatus.LOGGING_IN);
		login(username, password)
			.then((token) => {
				setAccessToken(token);
				setSigninStatus(SigninStatus.LOGGED_IN);
			})
			.catch((err) => {
				setSigninStatus(SigninStatus.NOT_LOGGED_IN);
				notifications.show({
					title: "Error",
					message: err.message,
					color: "red",
				});
			});
	};

	if (
		signinStatus === SigninStatus.NOT_LOGGED_IN ||
		signinStatus === SigninStatus.LOGGING_IN
	) {
		return (
			<Stack style={style} mt={100}>
				<h1>Welcome to TeraStore</h1>
				<Card
					shadow="xl"
					withBorder
					padding="xl"
					style={{ minWidth: 400 }}
					pos={"relative"}
				>
					<LoadingOverlay visible={signinStatus === SigninStatus.LOGGING_IN} />
					<h2>Sign in</h2>
					<form onSubmit={handleLogin}>
						<TextInput
							required
							type="email"
							placeholder="Email"
							value={username}
							onChange={(event) => setUsername(event.currentTarget.value)}
							pt={10}
							pb={10}
						/>
						<TextInput
							required
							type="password"
							placeholder="Password"
							value={password}
							onChange={(event) => setPassword(event.currentTarget.value)}
							pt={10}
							pb={10}
						/>
						<Button type="submit" fullWidth pt={10} pb={10}>
							Sign in
						</Button>
						<Box pt={20}>
							<Link to="/register">Create an account</Link>
						</Box>
					</form>
				</Card>
			</Stack>
		);
	} else if (signinStatus === SigninStatus.LOGGED_IN) {
		return <Navigate to={"/"} state={{ from: location }} replace />;
	}
}
