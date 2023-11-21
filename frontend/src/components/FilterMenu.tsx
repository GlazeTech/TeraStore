import * as M from "@mantine/core";
import {
	FilterResult,
	NumberAttrKey,
	PulseStringFilter,
	StringAttrKey,
} from "classes";
import { getFilterResultsForEachStringValue } from "helpers";
import { IAttrKey, Option } from "interfaces";
import { useEffect, useState } from "react";
import { useFiltersStore } from "store";
import { NumberFilterCard } from "./RecommendedFilterCard";

function selectValueFactory(pulseKey: IAttrKey) {
	if (pulseKey instanceof NumberAttrKey) {
		return <NumberFilterCard attrKey={pulseKey} />;
	} else if (pulseKey instanceof StringAttrKey) {
		return <SelectStringFilter selectedPulseKey={pulseKey} />;
	} else {
		throw new Error("Unhandled type of attr key");
	}
}

function SelectStringFilter({
	selectedPulseKey,
}: { selectedPulseKey: StringAttrKey }) {
	const [selectValueOptions, setSelectValueOptions] = useState<Option[]>([]);
	const [addPulseFilter, pulseFilters] = useFiltersStore((state) => [
		state.addPulseFilter,
		state.pulseFilters,
	]);

	// When a filter key is set, get available values and format a display value
	useEffect(() => {
		if (selectedPulseKey) {
			getFilterResultsForEachStringValue(selectedPulseKey, pulseFilters).then(
				(filterResults) => {
					setSelectValueOptions(filterResultsToOptions(filterResults));
				},
			);
		}
	}, [selectedPulseKey, pulseFilters]);

	const handleSelectValue = (value: string | null) => {
		if (selectedPulseKey && value) {
			addPulseFilter(new PulseStringFilter(selectedPulseKey, value));
		}
	};

	return (
		<M.Select
			label="Value"
			placeholder="Value"
			data={selectValueOptions}
			onChange={(value) => handleSelectValue(value)}
			disabled={!selectedPulseKey}
		/>
	);
}

function filterResultsToOptions(filterResults: FilterResult[]): Option[] {
	return filterResults.map((filter) => {
		if (filter.lastFilter instanceof PulseStringFilter) {
			return {
				value: filter.lastFilter.value,
				label: `${filter.lastFilter.value} (${filter.nPulses})`,
			};
		} else {
			throw new Error("Not implemented");
		}
	});
}

function FilterMenu() {
	const [newFilterIsOpen, setNewFilterIsOpen] = useState(false);
	const [selectedPulseKey, setSelectedPulseKey] = useState<IAttrKey | null>(
		null,
	);
	const [pulseKeys, pulseFilters, removePulseFilter] = useFiltersStore(
		(state) => [
			state.notAppliedPulseKeys,
			state.pulseFilters,
			state.removePulseFilter,
		],
	);

	// When a new filter is added, close the "New filter" if it was open.
	useEffect(() => {
		if (newFilterIsOpen) {
			setSelectedPulseKey(null);
			setNewFilterIsOpen(false);
		}
	}, [pulseFilters]);

	const handleDropdownChange = (key: string | null) => {
		if (pulseKeys) {
			const pulseKey = pulseKeys.find((el) => el.name === key);
			if (pulseKey) {
				setSelectedPulseKey(pulseKey);
			} else {
				throw new Error("Expected to find a pulse key, nothing found.");
			}
		}
	};

	return (
		<>
			<M.Popover opened={newFilterIsOpen} position="right-start" offset={5}>
				<M.Popover.Target>
					<M.Button
						m={5}
						onClick={() => setNewFilterIsOpen((o: boolean) => !o)}
					>
						New filter
					</M.Button>
				</M.Popover.Target>
				<M.Popover.Dropdown>
					<M.Select
						label="Key"
						placeholder="Key"
						data={pulseKeys?.map((e) => e.name)}
						value={selectedPulseKey?.name}
						onChange={handleDropdownChange}
					/>
					{selectedPulseKey && selectValueFactory(selectedPulseKey)}
				</M.Popover.Dropdown>
			</M.Popover>
			<div style={{ display: "flex", flexWrap: "wrap" }}>
				{pulseFilters.map((filter) => (
					<M.Pill
						m={5}
						key={filter.hash()}
						withRemoveButton
						onRemove={() => removePulseFilter(filter)}
					>
						{filter.displayFilter()}
					</M.Pill>
				))}
			</div>
		</>
	);
}

export default FilterMenu;
