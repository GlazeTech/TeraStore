import { AnnotatedPulse, AnnotatedPulseParsingError } from "classes";
import { BackendTHzDevice } from "interfaces";

export const makeFileID = (file: File) =>
	`${file.name}-${file.size}-${file.lastModified}`;

export function formatFileSize(fileSizeInBytes: number): string {
	if (fileSizeInBytes === 0) {
		return "0 bytes";
	}

	const sizes = ["bytes", "KB", "MB", "GB", "TB"];
	const i = Math.floor(Math.log10(fileSizeInBytes) / 3);

	return `${(fileSizeInBytes / 1000 ** i).toFixed(0)} ${sizes[i]}`;
}

export const readTextFile = (file: File) => {
	return new Promise((resolve, reject) => {
		const reader = new FileReader();
		reader.onload = (event) => {
			const fileContent = event.target?.result;
			resolve(fileContent);
		};
		reader.onerror = (error) => {
			reject(error);
		};
		reader.readAsText(file);
	});
};

export const filesAreIdentical = (A: File, B: File) => {
	return (
		A.name === B.name &&
		A.lastModified === B.lastModified &&
		A.size === B.size &&
		A.type === B.type
	);
};

export const extractPulses = (
	fileContent: unknown,
	devices: BackendTHzDevice[],
) => {
	if (typeof fileContent !== "string") {
		throw new AnnotatedPulseParsingError("file content is not a string");
	}

	let fileAsJSON: unknown;
	try {
		fileAsJSON = JSON.parse(fileContent);
	} catch (error) {
		throw new AnnotatedPulseParsingError("file content is not valid JSON");
	}

	let pulses: AnnotatedPulse[] = [];
	if (Array.isArray(fileAsJSON)) {
		pulses = fileAsJSON.map((pulse) =>
			AnnotatedPulse.validateAndParse(pulse, devices),
		);
	} else {
		pulses.push(AnnotatedPulse.validateAndParse(fileAsJSON, devices));
	}
	return pulses;
};
