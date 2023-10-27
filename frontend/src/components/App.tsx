import { AppShell, MantineProvider } from "@mantine/core";
import "@mantine/core/styles.css";
import "assets/App.css";
import { useEffect } from "react";
import { useFiltersStore } from "store";
import FilterMenu from "./FilterMenu";
import RecommendedFilters from "./RecommendedFilters";
function App() {
	const fetchInitialState = useFiltersStore((store) => store.fetchInitialState);

	useEffect(() => {
		fetchInitialState();
	}, []);

	return (
		<MantineProvider>
			<AppShell>
				<AppShell.Header> </AppShell.Header>
				<AppShell.Navbar>
					<FilterMenu />
				</AppShell.Navbar>
				<AppShell.Main>
					<RecommendedFilters />
				</AppShell.Main>
			</AppShell>
		</MantineProvider>
	);
}

export default App;
