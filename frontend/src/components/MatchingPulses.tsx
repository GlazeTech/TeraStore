import * as M from "@mantine/core";
import { getFilteredPulses, getPulse } from "api";
import { Pulse } from "classes";
import { useEffect, useState } from "react";
import { useFiltersStore } from "store";

interface PulseCardProps {
	pulseID: string;
	isSelected: boolean;
	setSelected: (value: React.SetStateAction<string | null>) => void;
}

function PulseCard({ pulseID, isSelected, setSelected }: PulseCardProps) {
	const [pulse, setPulse] = useState<Pulse | null>(null);

	useEffect(() => {
		if (isSelected) {
			getPulse(pulseID).then((p) => setPulse(p));
		}
	}, [isSelected]);

	return (
		<M.Popover
			opened={isSelected}
			position="left-start"
			offset={10}
			withArrow
			arrowSize={10}
		>
			<M.Popover.Target>
				<M.Card
					shadow="xs"
					radius="md"
					p={5}
					m={5}
					onClick={() =>
						isSelected ? setSelected(null) : setSelected(pulseID)
					}
					style={{
						backgroundColor: isSelected
							? "var(--mantine-color-blue-1)"
							: undefined,
					}}
				>
					<M.Text lineClamp={1}>{pulseID}</M.Text>
				</M.Card>
			</M.Popover.Target>
			<M.Popover.Dropdown>
				<M.Text>Datapoints: {pulse?.time.length}</M.Text>
				<M.Text>Integration Time: {pulse?.integrationTime} ms</M.Text>
				<M.Text>
					Creation Time: {pulse?.creationTime.toLocaleDateString("en-GB")}
				</M.Text>
			</M.Popover.Dropdown>
		</M.Popover>
	);
}

function MatchingPulses() {
	const [filteredPulses, setFilteredPulses] = useState<string[] | null>(null);
	const [selectedItem, setSelectedItem] = useState<string | null>(null);
	const [pulseFilters] = useFiltersStore((state) => [state.pulseFilters]);

	useEffect(() => {
		getFilteredPulses(pulseFilters).then((res) => setFilteredPulses(res));
	}, [pulseFilters]);

	return (
		<>
			<M.Stack p={10}>
				<M.Text fw={700} size="lg">
					Matching pulses: {filteredPulses?.length}
				</M.Text>
				<M.Button onClick={() => console.log("Not implemented yet")}>
					Download
				</M.Button>
			</M.Stack>

			<M.Divider ml={10} mr={10} />
			<M.ScrollArea type="hover">
				{filteredPulses?.map((pulseID) => (
					<PulseCard
						pulseID={pulseID}
						isSelected={pulseID === selectedItem}
						setSelected={setSelectedItem}
						key={pulseID}
					/>
				))}
			</M.ScrollArea>
		</>
	);
}

export default MatchingPulses;
