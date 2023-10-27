import { AppShell, MantineProvider } from "@mantine/core";
import "@mantine/core/styles.css";
import "assets/App.css";
import FilterMenu from "./FilterMenu";

function App() {
	return (
		<MantineProvider>
			<AppShell>
				<AppShell.Header> </AppShell.Header>
				<AppShell.Navbar>
					<FilterMenu />
				</AppShell.Navbar>
				<AppShell.Main>
					<h1>Hello, world!</h1>
				</AppShell.Main>
			</AppShell>
		</MantineProvider>
	);
}

export default App;
