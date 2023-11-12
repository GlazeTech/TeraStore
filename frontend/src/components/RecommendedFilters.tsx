import * as M from "@mantine/core";
import { FilterResult } from "classes";
import { getFilterResultsForEachStringValue } from "helpers";
import { IAttrKey } from "interfaces";
import { useEffect, useState } from "react";
import { useFiltersStore } from "store";

interface KeyFilterResult {
	key: IAttrKey;
	filterResults: FilterResult[];
}
interface RecommendedFilterCardProps {
	keyFilterResult: KeyFilterResult;
}
const totalPulses = (filterResultArr: FilterResult[]) =>
	filterResultArr.map((filter) => filter.nPulses).reduce((a, b) => a + b, 0);

function RecommendedFilterCard({
	keyFilterResult,
}: RecommendedFilterCardProps) {
	const [addPulseFilter] = useFiltersStore((state) => [state.addPulseFilter]);

	const addFilter = (idx: number) => {
		addPulseFilter(keyFilterResult.filterResults[idx].lastFilter);
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
					<M.Text fw={600}>{keyFilterResult.key.name}</M.Text>
					<M.Text>(total: {totalPulses(keyFilterResult.filterResults)})</M.Text>
				</M.Group>
			</M.Card.Section>
			<M.Card.Section withBorder inheritPadding>
				{keyFilterResult.filterResults.map((filterResult, idx) => (
					<M.Group
						mt="5"
						mb="5"
						justify="space-between"
						key={`filterResults-${idx}`}
					>
						<M.Badge variant="light" onClick={() => addFilter(idx)}>
							{filterResult.lastFilter.displayValue()}
						</M.Badge>
						<M.Text fw={400}>({filterResult.nPulses})</M.Text>
					</M.Group>
				))}
			</M.Card.Section>
		</M.Card>
	);
}

function RecommendedFilters() {
	const [notAppliedPulseKeys, pulseFilters] = useFiltersStore((state) => [
		state.notAppliedPulseKeys,
		state.pulseFilters,
	]);
	const [sortedFilterResults, setSortedFilterResults] = useState<
		KeyFilterResult[] | null
	>(null);

	useEffect(() => {
		if (notAppliedPulseKeys) {
			Promise.all(
				notAppliedPulseKeys.map((key) =>
					getFilterResultsForEachStringValue(key, pulseFilters),
				),
			).then((results) =>
				setSortedFilterResults(
					notAppliedPulseKeys
						.map((key, idx) => ({
							key: key,
							filterResults: results[idx],
						}))
						.sort(
							(a, b) =>
								totalPulses(b.filterResults) - totalPulses(a.filterResults),
						),
				),
			);
		}
	}, [notAppliedPulseKeys]);

	return (
		<div style={{ display: "flex", flexWrap: "wrap" }}>
			{sortedFilterResults?.map((kfResult, idx) => {
				return (
					<RecommendedFilterCard
						key={`recommendedFilterCard-${idx}`}
						keyFilterResult={kfResult}
					/>
				);
			})}
		</div>
	);
}

export default RecommendedFilters;
