import { PulseFilter } from "interfaces";
import { vi } from "vitest";

export const mockApi = async () => {
	vi.mock("api", async () => {
		return {
			getPulseKeys: vi.fn(async () => ["mocked_key1", "mocked_key2"]),
			getKeyValues: vi.fn(async (key: string) => [
				`${key}_val1`,
				`${key}_val2`,
				`${key}_val3`,
			]),
			getFilteredPulses: vi.fn(async (_: PulseFilter[]) => [
				"pulseId1",
				"pulseId2",
			]),
			cachedGetKeyValues: vi.fn(async (key: string) => [
				`${key}_val1`,
				`${key}_val2`,
				`${key}_val3`,
			]),
			cachedGetFilteredPulses: vi.fn(async (_: PulseFilter[]) => [
				"pulseId1",
				"pulseId2",
			]),
		};
	});
};
