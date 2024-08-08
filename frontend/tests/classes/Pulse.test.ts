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
		device_id: "someID",
		pulse_attributes: [
			{ key: "key1", value: "value1" },
			{ key: "key2", value: 2 },
		],
	};
	const validPulseWSigErrors = {
		pulse: {
			time: [1, 2, 3],
			signal: [0.1, 0.2, 0.3],
			signal_err: [0.01, 0.02, 0.03],
		},
		integration_time_ms: 100,
		creation_time: "2023-11-19T01:30:10.175Z",
		device_id: "someID",
		pulse_attributes: [
			{ key: "key1", value: "value1" },
			{ key: "key2", value: 2 },
		],
	};
	const devices = [
		{ device_id: "someID", serial_number: "someName" } as BackendTHzDevice,
	];

	test("should create an instance of AnnotatedPulse", () => {
		const annotatedPulse = AnnotatedPulse.validateAndParse(
			validAnnotatedPulse,
			devices,
		);

		expect(annotatedPulse).toBeInstanceOf(AnnotatedPulse);
		expect(annotatedPulse.pulse.time).toEqual(validAnnotatedPulse.pulse.time);
		expect(annotatedPulse.pulse.signal).toEqual(
			validAnnotatedPulse.pulse.signal,
		);
		expect(annotatedPulse.integration_time_ms).toEqual(
			validAnnotatedPulse.integration_time_ms,
		);
		expect(annotatedPulse.creation_time.toISOString()).toEqual(
			validAnnotatedPulse.creation_time,
		);
		expect(annotatedPulse.device_serial_number).toEqual(
			validAnnotatedPulse.device_id,
		);
		expect(annotatedPulse.pulse_attributes).toEqual(
			validAnnotatedPulse.pulse_attributes,
		);
	});

	test("should create an instance of AnnotatedPulse with errors", () => {
		const annotatedPulse = AnnotatedPulse.validateAndParse(
			validPulseWSigErrors,
			devices,
		);

		expect(annotatedPulse).toBeInstanceOf(AnnotatedPulse);
		expect(annotatedPulse.pulse.signal_err).toEqual(
			validPulseWSigErrors.pulse.signal_err,
		);
	});

	test("should fail when using wrong device ID", () => {
		expect(() => {
			AnnotatedPulse.validateAndParse(
				validAnnotatedPulse,
				// mocked devices
				[
					{
						device_id: "nonexistent device",
						serial_number: "someName",
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
			device_serial_number: devices[0].serial_number,
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
			creation_time: "2023-11-19T01:30:10.175Z",
			device_id: devices[0].serial_number,
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
