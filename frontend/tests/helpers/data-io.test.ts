import {
	AnnotatedPulse,
	AnnotatedPulseParsingError,
	InvalidCreationTimeError,
	InvalidDeviceIDError,
} from "classes";
import fs from "fs";
import { extractPulses, formatFileSize } from "helpers/data-io";
import { BackendTHzDevice } from "interfaces";
import path from "path";
import { describe, expect, test } from "vitest";

describe("extractPulses", () => {
	const devices: BackendTHzDevice[] = [
		{ device_id: 1, friendly_name: "Device 1" },
		{ device_id: 2, friendly_name: "Device 2" },
	];

	const root = path.resolve(__dirname, "../../");
	const readFile = (name: string) =>
		fs.readFileSync(path.join(root, "tests", "testing-assets", name), "utf-8");

	test("should extract single pulse from file content succesfully", () => {
		const fileContent = readFile("valid-annotated-pulse.json");
		const result = extractPulses(fileContent, devices);
		expect(result.every((item) => item instanceof AnnotatedPulse)).toBe(true);
		expect(result.length).toBe(1);
	});

	test("should extract pulses from array in file content succesfully", () => {
		const fileContent = readFile("valid-annotated-pulse-list.json");
		const result = extractPulses(fileContent, devices);
		expect(result.every((item) => item instanceof AnnotatedPulse)).toBe(true);
		expect(result.length).toBe(2);
	});

	test("should throw an error if fileContent is not a string", () => {
		const fileContent = 123;
		expect(() => {
			extractPulses(fileContent, devices);
		}).toThrowError(AnnotatedPulseParsingError);
	});

	test("should throw an error if fileContent is not valid JSON", () => {
		const fileContent = "not valid JSON";
		expect(() => {
			extractPulses(fileContent, devices);
		}).toThrowError(AnnotatedPulseParsingError);
	});

	test("should throw error if date format is wrong", () => {
		expect(() => {
			extractPulses(readFile("annotated-pulse-wrong-date.json"), devices);
		}).toThrowError(InvalidCreationTimeError);
	});

	test("should throw error if device ID does not exist", () => {
		expect(() => {
			extractPulses(readFile("annotated-pulse-wrong-device-id.json"), devices);
		}).toThrowError(InvalidDeviceIDError);
	});

	test("should throw error if file is missing attributes", () => {
		expect(() => {
			extractPulses(readFile("invalid-annotated-pulse.json"), devices);
		}).toThrowError(AnnotatedPulseParsingError);
	});
});

describe("formatFileSize", () => {
	test("should return '0 bytes' when fileSizeInBytes is 0", () => {
		const fileSizeInBytes = 0;
		const result = formatFileSize(fileSizeInBytes);
		expect(result).toBe("0 bytes");
	});

	test("should return formatted file size in KB", () => {
		const fileSizeInBytes = 999e3;
		const result = formatFileSize(fileSizeInBytes);
		expect(result).toBe("999 KB");
	});

	test("should return formatted file size in MB", () => {
		const fileSizeInBytes = 127.79e6;
		const result = formatFileSize(fileSizeInBytes);
		expect(result).toBe("128 MB");
	});

	test("should return formatted file size in GB", () => {
		const fileSizeInBytes = 1e9;
		const result = formatFileSize(fileSizeInBytes);
		expect(result).toBe("1 GB");
	});

	test("should return formatted file size in TB", () => {
		const fileSizeInBytes = 11.4e12;
		const result = formatFileSize(fileSizeInBytes);
		expect(result).toBe("11 TB");
	});
});
