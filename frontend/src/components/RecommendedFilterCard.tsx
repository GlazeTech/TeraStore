import * as M from "@mantine/core";
import { DateInput, DateValue } from "@mantine/dates";
import {
	getFilterResultsForEachStringValue,
	getFilteredPulses,
	getKeyValues,
} from "api";
import {
	DateAttrKey,
	FilterResult,
	NumberAttrKey,
	PulseDateFilter,
	PulseNumberFilter,
	StringAttrKey,
} from "classes";
import { uniqueElements } from "helpers";
import { IAttrKey, SliderMark } from "interfaces";
import { useEffect, useState } from "react";
import { useStoreShallow } from "store";

export function recoCardContentFactory(key: IAttrKey) {
	if (key instanceof StringAttrKey) {
		return <StringFilterCard attrKey={key} />;
	} else if (key instanceof NumberAttrKey) {
		return <NumberFilterCard attrKey={key} />;
	} else if (key instanceof DateAttrKey) {
		return <DateFilterCard attrKey={key} />;
	} else {
		throw new Error("Unhandled card type encountered");
	}
}

export function RecommendedCard({
	attrKey,
	nPulses,
}: { attrKey: IAttrKey; nPulses: number }) {
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
					<M.Text fw={600}>{attrKey.name}</M.Text>
					<M.Text>(total: {nPulses})</M.Text>
				</M.Group>
			</M.Card.Section>
			<M.Card.Section withBorder inheritPadding>
				{recoCardContentFactory(attrKey)}
			</M.Card.Section>
		</M.Card>
	);
}

export function NumberFilterCard({ attrKey }: { attrKey: NumberAttrKey }) {
	const [attrValues, setAttrValues] = useState<number[] | null>(null);
	const [sliderMinValue, setSliderMinValue] = useState(0);
	const [nPulsesInRange, setNPulsesInRange] = useState<number | null>(null);
	const [sliderMaxValue, setSliderMaxValue] = useState(1);
	const [sliderPrecision, setSliderPrecision] = useState(0);
	const [sliderStepsize, setSliderStepsize] = useState<number | undefined>(
		undefined,
	);
	const [sliderMarks, setSliderMarks] = useState<SliderMark[] | undefined>(
		undefined,
	);
	const [displayValue, setDisplayValue] = useState<[number, number]>([0, 1]);
	const [selectedValue, setSelectedValue] = useState<[number, number]>([0, 1]);
	const [addPulseFilter, pulseFilters] = useStoreShallow((state) => [
		state.addPulseFilter,
		state.pulseFilters,
	]);

	// Get all values on key
	useEffect(() => {
		getKeyValues<number[]>(attrKey).then((values) =>
			setAttrValues(uniqueElements(values)),
		);
	}, [attrKey]);

	// Count number of pulses filter would hit
	useEffect(() => {
		if (attrValues) {
			getFilteredPulses([
				...pulseFilters,
				new PulseNumberFilter(attrKey, ...selectedValue),
			]).then((result) => setNPulsesInRange(result.nPulses));
		}
	}, [selectedValue, pulseFilters]);

	// Format slider according to values
	useEffect(() => {
		if (attrValues) {
			const max = Math.max(...attrValues);
			const min = Math.min(...attrValues);
			const sliderPrecision = getSliderPrecision(min, max);
			setSliderMaxValue(max);
			setSliderMinValue(min);
			setSliderStepsize(10 ** -sliderPrecision);
			setDisplayValue([min, max]);
			setSelectedValue([min, max]);
			setSliderPrecision(sliderPrecision);
			setSliderMarks(
				attrValues.map((value) => {
					return { value: value };
				}),
			);
		}
	}, [attrValues, pulseFilters]);

	const handleLowerChange = (value: string | number) => {
		if (typeof value === "string") {
			return;
		}
		const upper = selectedValue[1];
		const lower = Math.min(value, upper);
		setDisplayValue([lower, upper]);
		setSelectedValue([lower, upper]);
	};

	const handleUpperChange = (value: string | number) => {
		if (typeof value === "string") {
			return;
		}
		const lower = selectedValue[0];
		const upper = Math.max(lower, value);
		setDisplayValue([lower, upper]);
		setSelectedValue([lower, upper]);
	};

	return (
		<>
			<M.Group mt="5" mb="5" justify="space-between">
				<M.Button
					variant="light"
					size="compact-sm"
					onClick={() =>
						addPulseFilter(new PulseNumberFilter(attrKey, ...selectedValue))
					}
				>
					Apply
				</M.Button>
				<M.Text>({nPulsesInRange})</M.Text>
			</M.Group>
			<M.Group mt="5" mb="5" justify="space-between">
				<M.NumberInput
					label="Upper bound"
					size="xs"
					value={selectedValue[1]}
					min={sliderMinValue}
					max={sliderMaxValue}
					onChange={handleUpperChange}
					hideControls
				/>
			</M.Group>
			<M.Group mt="5" mb="5" justify="space-between">
				<M.NumberInput
					label="Lower bound"
					size="xs"
					value={selectedValue[0]}
					min={sliderMinValue}
					max={sliderMaxValue}
					onChange={handleLowerChange}
					hideControls
				/>
			</M.Group>

			<M.RangeSlider
				mb={10}
				mt={10}
				value={displayValue}
				onChange={setDisplayValue}
				onChangeEnd={setSelectedValue}
				minRange={0}
				step={sliderStepsize}
				min={sliderMinValue}
				max={sliderMaxValue}
				precision={sliderPrecision}
				disabled={sliderMinValue === sliderMaxValue}
				marks={sliderMarks}
			/>
		</>
	);
}

function StringFilterCard({ attrKey }: { attrKey: StringAttrKey }) {
	const [filterResults, setFilterResults] = useState<FilterResult[] | null>(
		null,
	);
	const [addPulseFilter, pulseFilters] = useStoreShallow((state) => [
		state.addPulseFilter,
		state.pulseFilters,
	]);

	// Apply a filter for each key value to get number of pulses each kv-pair would hit
	useEffect(() => {
		getFilterResultsForEachStringValue(attrKey, pulseFilters).then(
			(filterResults) => setFilterResults(filterResults),
		);
	}, [pulseFilters, attrKey]);

	return (
		<>
			{filterResults?.map((filterResult) => (
				<M.Group
					mt="5"
					mb="5"
					justify="space-between"
					key={filterResult.lastFilter.hash()}
				>
					<M.Button
						variant="light"
						size="compact-xs"
						onClick={() => addPulseFilter(filterResult.lastFilter)}
					>
						{filterResult.lastFilter.displayValue()}
					</M.Button>
					<M.Text fw={400}>({filterResult.nPulses})</M.Text>
				</M.Group>
			))}
		</>
	);
}

export function DateFilterCard({ attrKey }: { attrKey: DateAttrKey }) {
	const [allDates, setAllDates] = useState<Date[] | null>(null);
	const [nPulsesInRange, setNPulsesInRange] = useState<number | null>(null);
	const [selectedDates, setSelectedDates] = useState<[DateValue, DateValue]>([
		null,
		null,
	]);

	const [addPulseFilter, pulseFilters] = useStoreShallow((state) => [
		state.addPulseFilter,
		state.pulseFilters,
	]);

	// Get all dates
	useEffect(() => {
		getFilteredPulses(pulseFilters).then((results) => {
			setAllDates(
				results.pulsesMetadata
					.map((metadata) => metadata.creationTime)
					.sort((a, b) => a.getTime() - b.getTime()),
			);
		});
	}, [pulseFilters]);

	// Count number of pulses filter would hit
	useEffect(() => {
		if (selectedDates[0] && selectedDates[1]) {
			getFilteredPulses([
				...pulseFilters,
				new PulseDateFilter(attrKey, selectedDates[0], selectedDates[1]),
			]).then((result) => setNPulsesInRange(result.nPulses));
		}
	}, [selectedDates, pulseFilters]);

	// Set selected dates to min and max date, when dates have been fetched
	useEffect(() => {
		if (allDates && allDates.length > 0) {
			setSelectedDates([
				dateToEarliestTimeOfDay(allDates[0]),
				dateToLatestTimeOfDay(allDates[allDates.length - 1]),
			]);
		}
	}, [allDates]);

	const handeLowerDateChange = (value: DateValue) => {
		if (value) {
			setSelectedDates([dateToEarliestTimeOfDay(value), selectedDates[1]]);
		}
	};

	const handleUpperDateChange = (value: DateValue) => {
		if (value) {
			setSelectedDates([selectedDates[0], dateToLatestTimeOfDay(value)]);
		}
	};

	const addFilter = () => {
		if (selectedDates[0] && selectedDates[1]) {
			addPulseFilter(
				new PulseDateFilter(attrKey, selectedDates[0], selectedDates[1]),
			);
		}
	};
	return (
		<>
			<M.Group mt="5" mb="5" justify="space-between">
				<M.Button variant="light" size="compact-sm" onClick={addFilter}>
					Apply
				</M.Button>
				<M.Text>({nPulsesInRange})</M.Text>
			</M.Group>
			<DateInput
				value={selectedDates[1]}
				onChange={handleUpperDateChange}
				minDate={selectedDates[0] ? selectedDates[0] : undefined}
				maxDate={allDates ? allDates[allDates.length - 1] : undefined}
				label="Upper bound"
				placeholder="Date input"
				size="sm"
				valueFormat="YYYY-MM-DD"
				mt={5}
				mb={5}
			/>

			<DateInput
				value={selectedDates[0]}
				onChange={handeLowerDateChange}
				minDate={allDates ? allDates[0] : undefined}
				maxDate={selectedDates[1] ? selectedDates[1] : undefined}
				label="Lower bound"
				placeholder="Date input"
				size="sm"
				valueFormat="YYYY-MM-DD"
				mb={10}
			/>
		</>
	);
}

const getSliderPrecision = (min: number, max: number) => {
	return max - min > 0
		? Math.abs(Math.round(Math.min(Math.log10((max - min) / 100) - 0.5, 0)))
		: 0;
};

const dateToEarliestTimeOfDay = (date: Date) => {
	return new Date(date.getFullYear(), date.getMonth(), date.getDate(), 0, 0, 0);
};

const dateToLatestTimeOfDay = (date: Date) => {
	return new Date(
		date.getFullYear(),
		date.getMonth(),
		date.getDate(),
		23,
		59,
		59,
	);
};
