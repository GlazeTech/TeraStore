import * as M from "@mantine/core";
import { useDisclosure, useListState } from "@mantine/hooks";
import { notifications } from "@mantine/notifications";
import { getFilteredPulses, getPulse, getPulses } from "api";
import { Pulse } from "classes";
import { downloadJson } from "helpers";
import { PulseMetadata } from "interfaces";
import { useEffect, useState } from "react";
import { useFiltersStore } from "store";

function PulseCard({
	pulseMetadata,
	isSelected,
	setSelected,
}: {
	pulseMetadata: PulseMetadata;
	isSelected: boolean;
	setSelected: (value: React.SetStateAction<PulseMetadata | null>) => void;
}) {
	const [pulse, setPulse] = useState<Pulse | null>(null);

	useEffect(() => {
		if (isSelected) {
			getPulse(pulseMetadata.pulseID).then((p) => setPulse(p));
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
						isSelected ? setSelected(null) : setSelected(pulseMetadata)
					}
					style={{
						backgroundColor: isSelected
							? "var(--mantine-color-blue-1)"
							: undefined,
					}}
				>
					<M.Text lineClamp={1}>
						{pulseMetadata.creationTime.toISOString()}
					</M.Text>
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

function DownloadModalContent({
	pulsesMetadata,
}: { pulsesMetadata: PulseMetadata[] }) {
	const [allSelected, allSelectedHandler] = useDisclosure(true);
	const [pulses, pulsesHandlers] = useListState(
		pulsesMetadata.map((pulseMetadata) => {
			return { id: pulseMetadata.pulseID, isSelected: true };
		}),
	);

	const toggleSelectAll = () => {
		allSelectedHandler.toggle();
		pulsesHandlers.setState(
			pulses.map((pulse) => {
				return { id: pulse.id, isSelected: !allSelected };
			}),
		);
	};

	const downloadSelected = () => {
		const selectedPulses = pulses.filter((pulse) => pulse.isSelected);
		if (selectedPulses.length === 0) {
			notifications.show({
				title: "Download pulses",
				message: "No pulses selected. Select at least one pulse to download.",
				autoClose: 2500,
			});
			return;
		}
		getPulses(selectedPulses.map((pulse) => pulse.id)).then((result) => {
			downloadJson(result, "TeraStore - pulses");
		});
	};

	const selectPulse = (idx: number) => {
		pulsesHandlers.setItemProp(idx, "isSelected", !pulses[idx].isSelected);
	};

	return (
		<>
			<div style={{ height: "80vh", overflow: "hidden" }}>
				<M.Group justify="flex-start">
					<M.Button onClick={toggleSelectAll}>Select all</M.Button>
					<M.Button onClick={downloadSelected}>Download</M.Button>
				</M.Group>
				<M.Divider m={10} />
				<M.ScrollArea type="hover" style={{ height: "100%" }}>
					{pulses.map((pulse, idx) => {
						return (
							<M.Card
								key={pulse.id}
								shadow="xs"
								radius="md"
								m={5}
								p={5}
								style={{
									backgroundColor: pulse.isSelected
										? "var(--mantine-color-blue-1)"
										: undefined,
								}}
								onClick={() => selectPulse(idx)}
							>
								<M.Group key={pulse.id} justify="space-between">
									<M.Text lineClamp={1}>{pulse.id}</M.Text>
								</M.Group>
							</M.Card>
						);
					})}
				</M.ScrollArea>
			</div>
		</>
	);
}

function MatchingPulses() {
	const [filteredPulses, setFilteredPulses] = useState<PulseMetadata[] | null>(
		null,
	);
	const [selectedItem, setSelectedItem] = useState<PulseMetadata | null>(null);
	const [pulseFilters] = useFiltersStore((state) => [state.pulseFilters]);
	const [modalIsOpen, modalHandler] = useDisclosure(false);

	useEffect(() => {
		getFilteredPulses(pulseFilters).then((res) =>
			setFilteredPulses(
				[...res.pulsesMetadata].sort(
					(a, b) => a.creationTime.getTime() - b.creationTime.getTime(),
				),
			),
		);
	}, [pulseFilters]);

	return (
		<>
			<M.Modal
				opened={modalIsOpen}
				onClose={modalHandler.close}
				title="Download pulses"
			>
				{filteredPulses && (
					<DownloadModalContent pulsesMetadata={filteredPulses} />
				)}
			</M.Modal>
			<M.Stack p={10}>
				<M.Text fw={700} size="lg">
					Matching pulses: {filteredPulses?.length}
				</M.Text>
				<M.Button onClick={modalHandler.toggle}>Download</M.Button>
			</M.Stack>

			<M.Divider ml={10} mr={10} />
			<M.ScrollArea type="hover">
				{filteredPulses?.map((pulseMetadata) => (
					<PulseCard
						pulseMetadata={pulseMetadata}
						isSelected={pulseMetadata === selectedItem}
						setSelected={setSelectedItem}
						key={pulseMetadata.pulseID}
					/>
				))}
			</M.ScrollArea>
		</>
	);
}

export default MatchingPulses;
