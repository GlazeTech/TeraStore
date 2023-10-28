import * as M from "@mantine/core";
import { FilterResult } from "classes";
import { getFilterResultsForEachKeyValue } from "helpers";
import { useEffect, useState } from "react";
import { useFiltersStore } from "store";
interface RecommendedFilterCardProps {
	pulseKey: string;
}

function RecommendedFilterCard({ pulseKey }: RecommendedFilterCardProps) {
	const [filterResults, setFilterResults] = useState<FilterResult[] | null>(
		null,
	);
	const [pulseFilters, addPulseFilter] = useFiltersStore((state) => [
		state.pulseFilters,
		state.addPulseFilter,
	]);

	useEffect(() => {
		getFilterResultsForEachKeyValue(pulseKey, pulseFilters).then((results) => {
			setFilterResults(results);
		});
	}, [pulseFilters]);

	const totalPulses = () =>
		filterResults?.map((filter) => filter.nPulses).reduce((a, b) => a + b, 0);

	const addFilter = (idx: number) => {
		if (filterResults) {
			addPulseFilter({
				key: pulseKey,
				value: filterResults[idx].lastFilter.value,
			});
		}
	};
	return (
		<M.Card
			shadow="sm"
			padding="xs"
			radius="md"
			withBorder
			style={{ margin: 5 }}
		>
			<M.Card.Section withBorder inheritPadding>
				<M.Group justify="space-between" mt="md" mb="xs">
					<M.Text fw={600}>{pulseKey}</M.Text>
					<M.Text>(total: {totalPulses()})</M.Text>
				</M.Group>
			</M.Card.Section>
			<M.Card.Section withBorder inheritPadding>
				{filterResults?.map((filterResult, idx) => (
					<M.Group
						mt="5"
						mb="5"
						justify="space-between"
						key={`filterResults-${idx}`}
					>
						{/* <M.Text fw={400}> */}
						<M.Badge variant="light" onClick={() => addFilter(idx)}>
							{filterResult.lastFilter.value}
						</M.Badge>
						{/* </M.Text> */}

						<M.Text fw={400}>({filterResult.nPulses})</M.Text>
					</M.Group>
				))}
			</M.Card.Section>
		</M.Card>
	);
}

function RecommendedFilters() {
	const [notAppliedPulseKeys] = useFiltersStore((state) => [
		state.notAppliedPulseKeys,
	]);

	const cards = notAppliedPulseKeys?.map((key, idx) => {
		return (
			<RecommendedFilterCard
				pulseKey={key}
				key={`recommendedFilterCard-${idx}`}
			/>
		);
	});

	return <div style={{ display: "flex", flexWrap: "wrap" }}>{cards}</div>;
}

export default RecommendedFilters;
