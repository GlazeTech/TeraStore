import {
	Box,
	Button,
	Card,
	LoadingOverlay,
	Stack,
	TextInput,
} from "@mantine/core";
import { notifications } from "@mantine/notifications";
import { register } from "auth";
import { AxiosError } from "axios";
import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

enum SignupStatus {
	NOT_REGISTERED = 1,
	REGISTERING = 2,
	REGISTERED = 3,
}

const style = {
	alignItems: "center",
};

export default function Register() {
	const [email, setEmail] = useState("");
	const [password, setPassword] = useState("");
	const [signupStatus, setSignupStatus] = useState(SignupStatus.NOT_REGISTERED);
	const navigate = useNavigate();

	const handleRegister = (event: FormEvent<HTMLFormElement>) => {
		event.preventDefault();
		setSignupStatus(SignupStatus.REGISTERING);
		const refreshDuration = 1500;
		register(email, password)
			.then(() => {
				setSignupStatus(SignupStatus.REGISTERED);
				notifications.show({
					title: "Success",
					message:
						"Registration succesful! Once you are approved by an administrator, you will be able to log in.",
					autoClose: refreshDuration,
					color: "green",
				});
				setTimeout(() => {
					navigate("/login");
				}, refreshDuration);
			})
			.catch((err) => {
				let msg = "An error occurred";
				if (err instanceof AxiosError) {
					if (err.response?.status === 409) {
						msg = err.response?.data?.detail;
					}
				}
				setSignupStatus(SignupStatus.NOT_REGISTERED);
				notifications.show({
					title: "Error",
					message: msg,
					color: "red",
				});
			});
	};

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
				<LoadingOverlay visible={signupStatus === SignupStatus.REGISTERING} />
				<h2>Create Account</h2>
				<form onSubmit={handleRegister}>
					<TextInput
						required
						type="email"
						placeholder="Email"
						value={email}
						onChange={(event) => setEmail(event.currentTarget.value)}
						pt={10}
						pb={10}
						disabled={signupStatus !== SignupStatus.NOT_REGISTERED}
					/>
					<TextInput
						required
						type="password"
						placeholder="Password"
						value={password}
						onChange={(event) => setPassword(event.currentTarget.value)}
						pt={10}
						pb={10}
						disabled={signupStatus !== SignupStatus.NOT_REGISTERED}
					/>
					<Button type="submit" fullWidth pt={10} pb={10}>
						Register
					</Button>
					<Box pt={20}>
						<Link to="/login">Already have an account? Sign in</Link>
					</Box>
				</form>
			</Card>
		</Stack>
	);
}
