import { AnnotatedPulse, annotatedPulseSchema } from "classes";

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


export const processUploadFiles = async (
	verifiedFiles: File[],
	candidateFiles: File[]
) => {
	// Find new files that haven't been uploaded before
	const newFiles = candidateFiles.filter(
		(candidate) => !verifiedFiles.some((verified) => filesAreIdentical(candidate, verified))
	);

	// Read and extract pulses
	const accepted: File[] = [];
	const denied: File[] = [];
	let newPulses: AnnotatedPulse[] = [];
	return Promise.all(newFiles.map(readTextFile))
		.then((filesContent) => {
			filesContent.forEach((content, idx) => {
				try {
					newPulses = [...newPulses, ...extractPulses(content)];
					accepted.push(newFiles[idx]);
				} catch {
					// Fail if we can't parse files
					denied.push(newFiles[idx]);
				}
			});
		})
		.then(() => {
			return { accepted, denied, newPulses };
		});
};

const extractPulses = (fileContent: unknown) => {
	if (typeof fileContent !== "string") {
		throw new Error("fileContent is not a string");
	}

	const fileAsJSON = JSON.parse(fileContent);
	let pulses: AnnotatedPulse[] = [];
	if (Array.isArray(fileAsJSON)) {
		pulses = fileAsJSON.map((pulse) => annotatedPulseSchema.parse(pulse) as AnnotatedPulse);
	} else {
		pulses.push(annotatedPulseSchema.parse(fileAsJSON) as AnnotatedPulse);
	}
	return pulses;
};
