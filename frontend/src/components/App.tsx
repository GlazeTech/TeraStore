import { AppShell, Button, MantineProvider } from "@mantine/core";
import "@mantine/core/styles.css";
import { pingBackend } from "api";
import "assets/App.css";
import { useState } from "react";
import FilterMenu from "./FilterMenu";

function App() {
	const [backendMsg, setBackendMsg] = useState<string>("");

	const handleButtonClick = () => {
		pingBackend().then((msg) => setBackendMsg(msg));
	};

	return (
		<MantineProvider>
			<AppShell>
				<AppShell.Header> </AppShell.Header>
				<AppShell.Navbar>
					<FilterMenu />
				</AppShell.Navbar>
				<AppShell.Main>
					<h1>Hello, world!</h1>
					<Button
						onClick={handleButtonClick}
						color="primary"
						variant="outlined"
					>
						Click me
					</Button>
					<h2>{backendMsg}</h2>
				</AppShell.Main>
			</AppShell>
		</MantineProvider>
	);
}

export default App;
