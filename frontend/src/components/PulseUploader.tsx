import * as M from "@mantine/core";
import { Dropzone } from "@mantine/dropzone";
import { useDisclosure, useListState } from "@mantine/hooks";
import { notifications } from "@mantine/notifications";
import { getDevices, uploadPulses } from "api";
import AnnotatedPulseExample from "assets/valid-annotated-pulse-example.json";
import {
	AnnotatedPulse,
	AnnotatedPulseParsingError,
	InvalidCreationTimeError,
	InvalidDeviceIDError,
} from "classes";
import { downloadJson } from "helpers";
import {
	extractPulses,
	filesAreIdentical,
	formatFileSize,
	makeFileID,
	readTextFile,
} from "helpers/data-io";
import { BackendTHzDevice } from "interfaces/backend";
import { ReactNode, useEffect, useState } from "react";

enum UploaderState {
	IDLE = "idle",
	UPLOADING = "uploading",
}

interface LoadedFile {
	file: File;
	pulses: AnnotatedPulse[];
}
export default function PulseUploader() {
	const [uploaderState, setUploaderState] = useState<UploaderState>(
		UploaderState.IDLE,
	);
	const [modalIsOpen, modalHandler] = useDisclosure(true);
	const [selectedFiles, selectedFilesHandlers] = useListState<LoadedFile>([]);
	const [pulses, pulsesHandler] = useListState<AnnotatedPulse>([]);
	const [devices, setDevices] = useState<BackendTHzDevice[] | null>(null);

	// Fetch devices
	useEffect(() => {
		getDevices().then((devices) => setDevices(devices));
	}, []);

	const handleDropFiles = (files: File[]) => {
		if (devices === null) {
			notifications.show({
				title: "No devices",
				message: "No devices found. Please contact an administrator.",
				autoClose: 2500,
				color: "red",
			});
			return;
		}

		processUploadFiles(selectedFiles, files, devices).then(
			({ accepted, errorNotificationContent }) => {
				// Show a notification about denied files
				errorNotificationContent.forEach((content) => {
					notifications.show({
						title: "Invalid file",
						message: content,
						autoClose: 2500,
						color: "red",
					});
				});
				selectedFilesHandlers.append(...accepted);
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

	const handleRemoveFile = (fileToDelete: LoadedFile) => {
		selectedFilesHandlers.filter(
			(file) => !filesAreIdentical(fileToDelete.file, file.file),
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
						{selectedFiles.map((selected) => (
							<File
								file={selected}
								key={makeFileID(selected.file)}
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
}: { file: LoadedFile; deleteHandler: (file: LoadedFile) => void }) {
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
					<M.Text>{file.file.name}</M.Text>
					<M.Text c={"dimmed"}>
						{`(${file.pulses.length}
						${file.pulses.length > 1 ? "pulses" : "pulse"},
						${formatFileSize(file.file.size)})`}
					</M.Text>
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

export const processUploadFiles = async (
	verifiedFiles: LoadedFile[],
	candidateFiles: File[],
	devices: BackendTHzDevice[],
) => {
	// Find new files that haven't been uploaded before
	const newFiles = candidateFiles.filter(
		(candidate) =>
			!verifiedFiles.some((verified) =>
				filesAreIdentical(candidate, verified.file),
			),
	);

	// Read and extract pulses
	const accepted: LoadedFile[] = [];
	const errorNotificationContent: ReactNode[] = [];
	return Promise.all(newFiles.map(readTextFile))
		.then((filesContent) => {
			filesContent.forEach((content, idx) => {
				try {
					accepted.push({
						file: newFiles[idx],
						pulses: extractPulses(content, devices),
					});
				} catch (error) {
					errorNotificationContent.push(
						errorNotificationFactory(newFiles[idx], error as Error),
					);
				}
			});
		})
		.then(() => {
			return { accepted, errorNotificationContent };
		});
};

const errorNotificationFactory = (file: File, error: Error): ReactNode => {
	if (error instanceof AnnotatedPulseParsingError) {
		return <ParseErrorNotifContent deniedFile={file} />;
	} else if (
		error instanceof InvalidDeviceIDError ||
		error instanceof InvalidCreationTimeError
	) {
		return `At least 1 pulse could not be parsed: ${error.message}`;
	} else {
		return error.message;
	}
};

const ParseErrorNotifContent = ({ deniedFile }: { deniedFile: File }) => {
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
				<M.Button size="xs" variant="subtle" onClick={handleClick}>
					<M.Text size="sm" c={"var(--mantine-color-pink-6)"}>
						Click here to download an example file.
					</M.Text>
				</M.Button>
			</M.Card.Section>
		</M.Card>
	);
};
