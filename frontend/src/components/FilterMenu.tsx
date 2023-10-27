import * as M from "@mantine/core";
import { getFilteredPulses, getKeyValues, getPulseKeys } from "api";
import { PulseFilter } from "interfaces";
import { useEffect, useState } from "react";

interface Option {
	value: string;
	label: string;
}

function FilterMenu() {
	const [newFilterIsOpen, setNewFilterIsOpen] = useState(false);
	const [nPulses, setNPulses] = useState<number | null>(null);
	const [pulseKeys, setPulseKeys] = useState<string[]>([]);
	const [selectedPulseKey, setSelectedPulseKey] = useState<string | null>(null);
	const [keyValues, setKeyValues] = useState<string[]>([]);
	const [selectedKeyValue, setSelectedKeyValue] = useState<string | null>(null);
	const [selectValueOptions, setSelectValueOptions] = useState<Option[]>([]);
	const [pulseFilters, setPulseFilters] = useState<PulseFilter[]>([]);

	// When "New filter" is clicked, get and set available keys to filter on
	useEffect(() => {
		if (newFilterIsOpen) {
			const currentFilters = pulseFilters.map((filter) => filter.key);
			getPulseKeys().then((keys) =>
				setPulseKeys(keys.filter((key) => !currentFilters.includes(key))),
			);
		}
	}, [newFilterIsOpen]);

	// When a filter key is set, get and set available values
	useEffect(() => {
		if (selectedPulseKey) {
			getKeyValues(selectedPulseKey).then((values) => setKeyValues(values));
		}
	}, [selectedPulseKey]);

	// When the values of a selected key are fetched, set the available value options with a formatted display value
	useEffect(() => {
		if (selectedPulseKey) {
			const pulsesForEachValue = keyValues.map(async (value) => {
				return getFilteredPulses([
					...pulseFilters,
					{ key: selectedPulseKey, value: value },
				]);
			});
			Promise.all(pulsesForEachValue).then((results) => {
				setSelectValueOptions(
					keyValues.map((value, idx) => {
						return { value: value, label: `${value} (${results[idx].length})` };
					}),
				);
			});
		}
	}, [keyValues]);

	// When the value of a key is selected, add the filter and close the "add filter" menu
	useEffect(() => {
		if (selectedPulseKey && selectedKeyValue) {
			setPulseFilters([
				...pulseFilters,
				{ key: selectedPulseKey, value: selectedKeyValue },
			]);
			setNewFilterIsOpen(false);
			setSelectedPulseKey(null);
			setSelectedKeyValue(null);
		}
	}, [selectedPulseKey, selectedKeyValue]);

	useEffect(() => {
		getFilteredPulses(pulseFilters).then((pulses) => setNPulses(pulses.length));
	}, [pulseFilters]);

	const removeFilter = (filterToDelete: string) => () => {
		setPulseFilters(
			pulseFilters.filter((filter) => filter.key !== filterToDelete),
		);
	};

	const displayPulseFilters = (filters: PulseFilter[]) => {
		return filters.map((filter) => (
			<M.Pill
				key={filter.key}
				withRemoveButton
				onRemove={removeFilter(filter.key)}
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
			Number of pulses: {nPulses === null ? "Apply filter" : nPulses}
		</>
	);
}

export default FilterMenu;
