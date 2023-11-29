import { readTestingAsset } from "@tests/testing-utils";
import {
	AnnotatedPulse,
	AnnotatedPulseParsingError,
	InvalidCreationTimeError,
	InvalidDeviceIDError,
} from "classes";
import { extractPulses, formatFileSize } from "helpers/data-io";
import { BackendTHzDevice } from "interfaces";
import { describe, expect, test } from "vitest";

describe("extractPulses", () => {
	const devices: BackendTHzDevice[] = [
		{
			device_id: "5042dbda-e9bc-4216-a614-ac56d0a32023",
			friendly_name: "Device 1",
		},
		{
			device_id: "5042dbda-e9bc-4216-a614-ac56d0a32023",
			friendly_name: "Device 2",
		},
	];

	test("should extract single pulse from file content succesfully", () => {
		const fileContent = readTestingAsset("valid-annotated-pulse.json");
		const result = extractPulses(fileContent, devices);
		expect(result.every((item) => item instanceof AnnotatedPulse)).toBe(true);
		expect(result.length).toBe(1);
	});

	test("should extract pulses from array in file content succesfully", () => {
		const fileContent = readTestingAsset("valid-annotated-pulse-list.json");
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
			extractPulses(
				readTestingAsset("annotated-pulse-wrong-date.json"),
				devices,
			);
		}).toThrowError(InvalidCreationTimeError);
	});

	test("should throw error if device ID does not exist", () => {
		expect(() => {
			extractPulses(
				readTestingAsset("annotated-pulse-wrong-device-id.json"),
				devices,
			);
		}).toThrowError(InvalidDeviceIDError);
	});

	test("should throw error if file is missing attributes", () => {
		expect(() => {
			extractPulses(readTestingAsset("invalid-annotated-pulse.json"), devices);
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
