import { AppShell, Divider } from "@mantine/core";
import { useEffect } from "react";
import { useStoreShallow } from "store";
import FilterMenu from "./FilterMenu";
import Header from "./Header";
import MatchingPulses from "./MatchingPulses";
import PulseUploader from "./PulseUploader";
import RecommendedFilters from "./RecommendedFilters";

function App() {
	const fetchInitialState = useStoreShallow((store) => store.fetchInitialState);

	useEffect(() => {
		fetchInitialState();
	}, []);

	return (
		<AppShell
			header={{ height: 50 }}
			navbar={{ width: 250, breakpoint: "xs" }}
			aside={{ width: 250, breakpoint: "xs" }}
		>
			<AppShell.Header>
				<Header />
			</AppShell.Header>
			<AppShell.Navbar>
				<PulseUploader />
				<Divider m={5} />
				<FilterMenu />
			</AppShell.Navbar>
			<AppShell.Main>
				<RecommendedFilters />
			</AppShell.Main>
			<AppShell.Aside>
				<MatchingPulses />
			</AppShell.Aside>
		</AppShell>
	);
}

export default App;
