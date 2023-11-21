import * as M from "@mantine/core";
import { Dropzone } from "@mantine/dropzone";
import { useDisclosure, useListState } from "@mantine/hooks";
import { notifications } from "@mantine/notifications";
import { uploadPulses } from "api";
import AnnotatedPulseExample from "assets/valid-annotated-pulse-example.json";
import { AnnotatedPulse } from "classes";
import { downloadJson } from "helpers";
import {
	filesAreIdentical,
	formatFileSize,
	makeFileID,
	processUploadFiles,
} from "helpers/data-io";
import { useState } from "react";

enum UploaderState {
	IDLE = "idle",
	UPLOADING = "uploading",
}

export default function PulseUploader() {
	const [uploaderState, setUploaderState] = useState<UploaderState>(
		UploaderState.IDLE,
	);
	const [modalIsOpen, modalHandler] = useDisclosure(true);
	const [selectedFiles, selectedFilesHandlers] = useListState<File>([]);
	const [pulses, pulsesHandler] = useListState<AnnotatedPulse>([]);

	const handleDropFiles = (files: File[]) => {
		processUploadFiles(selectedFiles, files).then(
			({ accepted, denied, newPulses }) => {
				// Show a notification about denied files
				denied.forEach((deniedFile) => {
					notifications.show({
						title: "Invalid file",
						message: <ErrorNotificationContent deniedFile={deniedFile} />,
						autoClose: 2500,
						color: "red",
					});
				});
				selectedFilesHandlers.append(...accepted);
				pulsesHandler.append(...newPulses);
			},
		);
	};

	const handleRejectFiles = (msg: string) => {
		notifications.show({
			title: "Wrong format",
			message: msg,
			autoClose: 2500,
			color: "red",
		});
	};

	const handleRemoveFile = (fileToDelete: File) => {
		selectedFilesHandlers.filter(
			(file) => !filesAreIdentical(fileToDelete, file),
		);
	};

	const handleUpload = () => {
		if (selectedFiles.length === 0) {
			notifications.show({
				title: "Missing files",
				message: "Select at least 1 file for upload.",
				autoClose: 2500,
				color: "red",
			});
			return;
		}
		setUploaderState(UploaderState.UPLOADING);
		uploadPulses(pulses).then((_) => {
			notifications.show({
				title: "Upload completed",
				message: `Uploaded ${pulses.length} ${
					pulses.length > 1 ? "pulses" : "pulse"
				} successfully!`,
				autoClose: 2500,
				color: "green",
			});
			setUploaderState(UploaderState.IDLE);
			selectedFilesHandlers.setState([]);
			pulsesHandler.setState([]);
			modalHandler.toggle();
		});
	};

	return (
		<>
			<M.Modal
				opened={modalIsOpen}
				onClose={modalHandler.close}
				title="Upload pulses"
				size={"lg"}
			>
				<Dropzone
					onDrop={handleDropFiles}
					onReject={() => handleRejectFiles("Files must be JSON-files.")}
					accept={["application/json"]}
					maxSize={50 * 1024 * 1024}
					mih={200}
				>
					<DropzoneText />
				</Dropzone>
				<M.Button
					mt={15}
					mb={10}
					fullWidth
					onClick={handleUpload}
					disabled={
						uploaderState === UploaderState.UPLOADING ||
						selectedFiles.length === 0
					}
				>
					{uploaderState === UploaderState.UPLOADING ? (
						<M.Loader size={"sm"} />
					) : (
						"Upload"
					)}
				</M.Button>
				<div style={{ height: "40vh", overflow: "hidden" }}>
					<M.ScrollArea type="hover" style={{ height: "100%" }}>
						{selectedFiles.map((file) => (
							<File
								file={file}
								key={makeFileID(file)}
								deleteHandler={handleRemoveFile}
							/>
						))}
					</M.ScrollArea>
				</div>
			</M.Modal>
			<M.Button m={5} onClick={modalHandler.toggle}>
				Upload
			</M.Button>
		</>
	);
}

function File({
	file,
	deleteHandler,
}: { file: File; deleteHandler: (key: File) => void }) {
	return (
		<M.Card
			p={5}
			mt={5}
			style={{
				backgroundColor: "var(--mantine-color-gray-1)",
			}}
		>
			<M.Group justify="space-between">
				<M.Group>
					<M.Text>{file.name}</M.Text>
					<M.Text c={"dimmed"}>({formatFileSize(file.size)})</M.Text>
				</M.Group>
				<M.CloseButton onClick={() => deleteHandler(file)} />
			</M.Group>
		</M.Card>
	);
}

const DropzoneText = () => (
	<M.Stack>
		<M.Group justify="center">
			<M.Text size="xl" inline>
				Drag files here or click to select
			</M.Text>
		</M.Group>
		<M.Group justify="center">
			<M.Text size="sm" c="dimmed" inline mt={7}>
				File format should be JSON.
			</M.Text>
		</M.Group>
		<M.Group justify="center">
			<M.Text size="sm" c="dimmed" inline mt={7}>
				Attach as many files as you like.
			</M.Text>
		</M.Group>
	</M.Stack>
);

const ErrorNotificationContent = ({ deniedFile }: { deniedFile: File }) => {
	const handleClick = () => {
		downloadJson(AnnotatedPulseExample, "annotated-pulses-example.json");
	};
	return (
		<M.Card>
			<M.Card.Section>
				<M.Text size="sm">{`Could not parse file "${deniedFile.name}."`}</M.Text>
			</M.Card.Section>
			<M.Card.Section>
				<M.Badge
					variant="light"
					color="pink"
					mr={10}
					mt={10}
					mb={10}
					onClick={handleClick}
				>
					Tip
				</M.Badge>
				<M.UnstyledButton size="sm" onClick={handleClick}>
					<M.Text size="sm">Click here to download an example file.</M.Text>
				</M.UnstyledButton>
			</M.Card.Section>
		</M.Card>
	);
};
