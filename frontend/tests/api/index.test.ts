import { loginAsAdmin, readTestingAsset } from "@tests/testing-utils";
import { getFilteredPulses, getPulseKeys, getPulses } from "api";
import { uploadPulses } from "api";
import {
	AnnotatedPulse,
	DateAttrKey,
	FilterResult,
	PulseDateFilter,
	PulseNumberFilter,
	PulseStringFilter,
} from "classes";
import { extractPulses } from "helpers/data-io";
import { KVType, PulseFilter } from "interfaces";
import { BackendTHzDevice } from "interfaces";
import { describe, expect, test } from "vitest";

describe("getFilteredPulses", async () => {
	await loginAsAdmin();
	const pulseKeys = await getPulseKeys();

	test("no filters should return all pulses", async () => {
		const filters: PulseFilter[] = [];
		const result = await getFilteredPulses(filters);
		expect(result.nPulses).toBeGreaterThan(0);
	});

	test("should work with a number filter", async () => {
		const firstNumberKey = pulseKeys.find((key) => key.type === KVType.NUMBER);
		if (!firstNumberKey) {
			throw new Error("No number keys found");
		}
		const filters: PulseFilter[] = [
			new PulseNumberFilter(firstNumberKey, 0, 1),
		];
		const result = await getFilteredPulses(filters);
		expect(result).toBeInstanceOf(FilterResult);
	});

	test("should work with a string filter", async () => {
		const firstStringKey = pulseKeys.find((key) => key.type === KVType.STRING);
		if (!firstStringKey) {
			throw new Error("No number keys found");
		}

		const filters: PulseFilter[] = [
			new PulseStringFilter(firstStringKey, "something"),
		];
		const result = await getFilteredPulses(filters);
		expect(result).toBeInstanceOf(FilterResult);
	});

	test("should work with a date filter", async () => {
		const filters: PulseFilter[] = [
			new PulseDateFilter(
				new DateAttrKey("date"),
				new Date("1900-01-01"),
				new Date("2100-01-01"),
			),
		];
		const result = await getFilteredPulses(filters);
		expect(result).toBeInstanceOf(FilterResult);
		expect(result.nPulses).toBeGreaterThan(0);
	});
});

describe("uploadPulses", () => {
	const devices: BackendTHzDevice[] = [
		{
			friendly_name: "My friendly device",
			device_id: "5042dbda-e9bc-4216-a614-ac56d0a32023",
		},
	];

	test("should upload single pulse successfully", async () => {
		const pulses = extractPulses(
			readTestingAsset("valid-annotated-pulse.json"),
			devices,
		);
		const result = await uploadPulses(pulses);
		expect(Array.isArray(result)).toBe(true);
		if (result) {
			expect(result.length).toBe(pulses.length);
			expect(typeof result[0]).toBe("string");
		}
	});

	test("should upload multiple pulses successfully", async () => {
		const pulses = extractPulses(
			readTestingAsset("valid-annotated-pulse-list.json"),
			devices,
		);
		const result = await uploadPulses(pulses);
		expect(Array.isArray(result)).toBe(true);
		if (result) {
			expect(result.length).toBe(pulses.length);
			expect(typeof result[0]).toBe("string");
		}
	});
});

describe("getPulses", () => {
	test("should return annotated pulses", async () => {
		const allPulses = await getFilteredPulses([]);
		const downloadablePulses = await getPulses(
			allPulses.pulsesMetadata.map((p) => p.pulseID).slice(0, 5),
		);
		downloadablePulses.forEach((pulse) => {
			expect(pulse).toBeInstanceOf(AnnotatedPulse);
			expect(pulse.pulse.time).toBeDefined();
			expect(pulse.pulse.signal).toBeDefined();
			expect(pulse.pulse.signal_err).toBeDefined();
			expect(pulse.pulse_attributes).toBeDefined();
			expect(pulse.device_id).toBeDefined();
			expect(pulse.integration_time_ms).toBeDefined();
			expect(pulse.pulse).toBeDefined();
			expect(pulse.pulse_id).toBeDefined();
		});
	});
});
