import * as M from "@mantine/core";
import { getFilteredPulses, getKeyValues } from "api";
import {
	FilterResult,
	NumberAttrKey,
	PulseNumberFilter,
	StringAttrKey,
} from "classes";
import { getFilterResultsForEachStringValue, uniqueElements } from "helpers";
import { IAttrKey, SliderMark } from "interfaces";
import { useEffect, useState } from "react";
import { useFiltersStore } from "store";

export function recoCardContentFactory(key: IAttrKey) {
	if (key instanceof StringAttrKey) {
		return <StringFilterCard attrKey={key} />;
	} else if (key instanceof NumberAttrKey) {
		return <NumberFilterCard attrKey={key} />;
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
	const [addPulseFilter, pulseFilters] = useFiltersStore((state) => [
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
				<M.Text>Upper bound</M.Text>
				<M.NumberInput
					size="xs"
					value={selectedValue[1]}
					min={sliderMinValue}
					max={sliderMaxValue}
					onChange={handleUpperChange}
					hideControls
				/>
			</M.Group>
			<M.Group mt="5" mb="5" justify="space-between">
				<M.Text>Lower bound</M.Text>
				<M.NumberInput
					size="xs"
					value={selectedValue[0]}
					min={sliderMinValue}
					max={sliderMaxValue}
					onChange={handleLowerChange}
					hideControls
				/>
			</M.Group>

			<M.RangeSlider
				m={10}
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
	const [addPulseFilter, pulseFilters] = useFiltersStore((state) => [
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

const getSliderPrecision = (min: number, max: number) => {
	return max - min > 0
		? Math.abs(Math.round(Math.min(Math.log10((max - min) / 100) - 0.5, 0)))
		: 0;
};
