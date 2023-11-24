import { FilterResult, attrKeyFactory } from "classes";
import { BackendTHzDevice, IAttrKey, KVType, PulseFilter } from "interfaces";
import { vi } from "vitest";

export const mockApi = async () => {
	vi.mock("api", async () => {
		return {
			getPulseKeys: vi.fn(
				async (): Promise<IAttrKey[]> => [
					attrKeyFactory("mocked_key1", KVType.STRING),
					attrKeyFactory("mocked_key2", KVType.STRING),
				],
			),
			getKeyValues: vi.fn(
				async (key: IAttrKey): Promise<string[]> => [
					`${key.name}_val1`,
					`${key.name}_val2`,
					`${key.name}_val3`,
				],
			),
			getFilteredPulses: vi.fn(
				async (filters: PulseFilter[]): Promise<FilterResult> =>
					new FilterResult(filters, []),
			),
			getDevices: vi.fn(async (): Promise<BackendTHzDevice[]> => []),
		};
	});
};
