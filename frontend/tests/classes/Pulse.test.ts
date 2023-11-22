import {
	AnnotatedPulse,
	AnnotatedPulseParsingError,
	InvalidCreationTimeError,
	InvalidDeviceIDError,
} from "classes";
import { BackendTHzDevice } from "interfaces";
import { describe, expect, test } from "vitest";

describe("AnnotatedPulse", () => {
	const validAnnotatedPulse = {
		pulse: {
			time: [1, 2, 3],
			signal: [0.1, 0.2, 0.3],
		},
		integration_time_ms: 100,
		creation_time: "2023-11-19T01:30:10.175Z",
		device_id: 1,
		pulse_attributes: [
			{ key: "key1", value: "value1" },
			{ key: "key2", value: 2 },
		],
	};
	const devices = [{ device_id: 1, friendly_name: "someName" }];

	test("should create an instance of AnnotatedPulse", () => {
		const annotatedPulse = AnnotatedPulse.validateAndParse(
			validAnnotatedPulse,
			devices,
		);

		expect(annotatedPulse).toBeInstanceOf(AnnotatedPulse);
		expect(annotatedPulse.pulse).toEqual(validAnnotatedPulse.pulse);
		expect(annotatedPulse.integration_time_ms).toEqual(
			validAnnotatedPulse.integration_time_ms,
		);
		expect(annotatedPulse.creation_time.toISOString()).toEqual(
			validAnnotatedPulse.creation_time,
		);
		expect(annotatedPulse.device_id).toEqual(validAnnotatedPulse.device_id);
		expect(annotatedPulse.pulse_attributes).toEqual(
			validAnnotatedPulse.pulse_attributes,
		);
	});

	test("should validate and parse data", () => {
		const parsedPulse = AnnotatedPulse.validateAndParse(
			validAnnotatedPulse,
			devices,
		);

		expect(parsedPulse).toBeInstanceOf(AnnotatedPulse);
		expect(parsedPulse.pulse).toEqual(validAnnotatedPulse.pulse);
		expect(parsedPulse.integration_time_ms).toEqual(
			validAnnotatedPulse.integration_time_ms,
		);
		expect(parsedPulse.creation_time.toISOString()).toEqual(
			validAnnotatedPulse.creation_time,
		);
		expect(parsedPulse.device_id).toEqual(validAnnotatedPulse.device_id);
		expect(parsedPulse.pulse_attributes).toEqual(
			validAnnotatedPulse.pulse_attributes,
		);
	});

	test("should fail when using wrong device ID", () => {
		const wrongDeviceId = -1; // Wrong device ID
		expect(() => {
			AnnotatedPulse.validateAndParse(
				validAnnotatedPulse,
				// mocked devices
				[
					{
						device_id: wrongDeviceId,
						friendly_name: "someName",
					} as BackendTHzDevice,
				],
			);
		}).toThrowError(InvalidDeviceIDError);
	});

	test("should throw an error for invalid creation_time", () => {
		const invalidAnnotatedPulse = {
			pulse: {
				time: [1, 2, 3],
				signal: [0.1, 0.2, 0.3],
			},
			integration_time_ms: 100,
			creation_time: "wrong datetime", // Invalid creation_time
			device_id: 1,
			pulse_attributes: [
				{ key: "key1", value: "value1" },
				{ key: "key2", value: 2 },
			],
		};
		expect(() => {
			AnnotatedPulse.validateAndParse(invalidAnnotatedPulse, devices);
		}).toThrowError(InvalidCreationTimeError);
	});

	test("should throw an error for invalid pulse", () => {
		const invalidAnnotatedPulse = {
			pulse: {
				time: [1, 2, 3],
			},
			integration_time_ms: 100,
			creation_time: "wrong datetime", // Invalid creation_time
			device_id: 1,
			pulse_attributes: [
				{ key: "key1", value: "value1" },
				{ key: "key2", value: 2 },
			],
		};
		expect(() => {
			AnnotatedPulse.validateAndParse(invalidAnnotatedPulse, devices);
		}).toThrowError(AnnotatedPulseParsingError);
	});
});
