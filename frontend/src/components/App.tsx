import "@mantine/core/styles.css";
import "@mantine/notifications/styles.css";

import { AppShell, MantineProvider } from "@mantine/core";
import { Notifications } from "@mantine/notifications";
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
			<Notifications position="top-right" />
			<AppShell
				navbar={{ width: 250, breakpoint: "xs" }}
				aside={{ width: 250, breakpoint: "xs" }}
			>
				<AppShell.Header> </AppShell.Header>
				<AppShell.Navbar>
					<FilterMenu />
				</AppShell.Navbar>
				<AppShell.Main>
					<RecommendedFilters />
				</AppShell.Main>
				<AppShell.Aside>
					<MatchingPulses />
				</AppShell.Aside>
			</AppShell>
		</MantineProvider>
	);
}

export default App;
