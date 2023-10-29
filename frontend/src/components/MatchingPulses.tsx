import * as M from "@mantine/core";
import { getFilteredPulses } from "api";
import { useEffect, useState } from "react";
import { useFiltersStore } from "store";
function MatchingPulses() {
	const [nPulses, setNPulses] = useState<number | null>(null);
	const [pulseFilters] = useFiltersStore((state) => [state.pulseFilters]);

	useEffect(() => {
		getFilteredPulses(pulseFilters).then((res) => setNPulses(res.length));
	}, [pulseFilters]);

	return (
		<M.Text fw={700} p={10} size="lg">
			Matching pulses: {nPulses}
		</M.Text>
	);
}

export default MatchingPulses;
