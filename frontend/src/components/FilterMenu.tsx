import * as M from "@mantine/core";
import { getFilteredPulses, getKeyValues } from "api";
import { PulseFilter } from "interfaces";
import { useEffect, useState } from "react";
import { useFiltersStore } from "store";
interface Option {
	value: string;
	label: string;
}

function FilterMenu() {
	const [newFilterIsOpen, setNewFilterIsOpen] = useState(false);
	const [selectedPulseKey, setSelectedPulseKey] = useState<string | null>(null);
	const [selectedKeyValue, setSelectedKeyValue] = useState<string | null>(null);
	const [selectValueOptions, setSelectValueOptions] = useState<Option[]>([]);
	const [pulseKeys, pulseFilters, addPulseFilter, removePulseFilter] =
		useFiltersStore((state) => [
			state.notAppliedPulseKeys,
			state.pulseFilters,
			state.addPulseFilter,
			state.removePulseFilter,
		]);

	// When a filter key is set, get available values and number of pulses each value hits
	useEffect(() => {
		if (selectedPulseKey) {
			getKeyValues(selectedPulseKey).then((values) => {
				const pulsesForEachValue = values.map(async (value) => {
					return getFilteredPulses([
						...pulseFilters,
						{ key: selectedPulseKey, value: value },
					]);
				});
				Promise.all(pulsesForEachValue).then((results) => {
					setSelectValueOptions(
						values.map((value, idx) => {
							return {
								value: value,
								label: `${value} (${results[idx].length})`,
							};
						}),
					);
				});
			});
		}
	}, [selectedPulseKey]);

	// When the value of a key is selected, add the filter and close the "add filter" menu
	useEffect(() => {
		if (selectedPulseKey && selectedKeyValue) {
			addPulseFilter({ key: selectedPulseKey, value: selectedKeyValue });
			setNewFilterIsOpen(false);
			setSelectedPulseKey(null);
			setSelectedKeyValue(null);
		}
	}, [selectedPulseKey, selectedKeyValue]);

	const displayPulseFilters = (filters: PulseFilter[]) => {
		return filters.map((filter) => (
			<M.Pill
				key={filter.key}
				withRemoveButton
				onRemove={() => removePulseFilter(filter)}
			>{`${filter.key}: ${filter.value}`}</M.Pill>
		));
	};

	return (
		<>
			<M.Popover opened={newFilterIsOpen} position="right-start" offset={5}>
				<M.Popover.Target>
					<M.Button onClick={() => setNewFilterIsOpen((o: boolean) => !o)}>
						New filter
					</M.Button>
				</M.Popover.Target>
				<M.Popover.Dropdown>
					<M.Select
						label="Key"
						placeholder="Key"
						data={pulseKeys}
						value={selectedPulseKey}
						onChange={setSelectedPulseKey}
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
			{displayPulseFilters(pulseFilters)}
		</>
	);
}

export default FilterMenu;
