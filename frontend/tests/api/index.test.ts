import { getFilteredPulses, getPulseKeys } from "api";
import {
	DateAttrKey,
	FilterResult,
	PulseDateFilter,
	PulseNumberFilter,
	PulseStringFilter,
} from "classes";
import { KVType, PulseFilter } from "interfaces";
import { describe, expect, test } from "vitest";

describe("getFilteredPulses", async () => {
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
