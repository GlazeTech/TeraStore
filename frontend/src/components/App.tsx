import { AppShell, MantineProvider } from "@mantine/core";
import "@mantine/core/styles.css";
import { useEffect } from "react";
import { useFiltersStore } from "store";
import FilterMenu from "./FilterMenu";
import MatchingPulses from "./MatchingPulses";
import RecommendedFilters from "./RecommendedFilters";
function App() {
	const fetchInitialState = useFiltersStore((store) => store.fetchInitialState);

	useEffect(() => {
		fetchInitialState();
	}, []);

	return (
		<MantineProvider defaultColorScheme="auto">
			<AppShell navbar={{ width: 200, breakpoint: "xs" }}>
				<AppShell.Header> </AppShell.Header>
				<AppShell.Navbar>
					<FilterMenu />
				</AppShell.Navbar>
				<AppShell.Main>
					<MatchingPulses />
					<RecommendedFilters />
				</AppShell.Main>
			</AppShell>
		</MantineProvider>
	);
}

export default App;
