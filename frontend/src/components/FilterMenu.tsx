import * as M from "@mantine/core";
import { FilterResult, PulseStringFilter } from "classes";
import { getFilterResultsForEachStringValue } from "helpers";
import { IAttrKey, Option, PulseFilter } from "interfaces";
import { useEffect, useState } from "react";
import { useFiltersStore } from "store";

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
	const [selectedKeyValue, setSelectedKeyValue] = useState<string | null>(null);
	const [selectValueOptions, setSelectValueOptions] = useState<Option[]>([]);
	const [pulseKeys, pulseFilters, addPulseFilter, removePulseFilter] =
		useFiltersStore((state) => [
			state.notAppliedPulseKeys,
			state.pulseFilters,
			state.addPulseFilter,
			state.removePulseFilter,
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
	}, [selectedPulseKey]);

	// When the value of a key is selected, add the filter and close the "add filter" menu
	useEffect(() => {
		if (selectedPulseKey && selectedKeyValue) {
			addPulseFilter(new PulseStringFilter(selectedPulseKey, selectedKeyValue));
			setNewFilterIsOpen(false);
			setSelectedPulseKey(null);
			setSelectedKeyValue(null);
		}
	}, [selectedPulseKey, selectedKeyValue]);
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

	const displayPulseFilters = (filters: PulseFilter[]) => {
		return filters.map((filter) => (
			<M.Pill
				m={5}
				key={filter.hash()}
				withRemoveButton
				onRemove={() => removePulseFilter(filter)}
			>
				{filter.displayFilter()}
			</M.Pill>
		));
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
					{selectedPulseKey ? (
						<M.Select
							label="Value"
							placeholder="Value"
							data={selectValueOptions}
							onChange={setSelectedKeyValue}
							disabled={!selectedPulseKey}
						/>
					) : (
						""
					)}
				</M.Popover.Dropdown>
			</M.Popover>
			<div style={{ display: "flex", flexWrap: "wrap" }}>
				{displayPulseFilters(pulseFilters)}
			</div>
		</>
	);
}

export default FilterMenu;
