import { fireEvent, render, waitFor } from "@tests/testing-utils";
import FilterMenu from "components/FilterMenu";
import { PulseFilter } from "interfaces";
import { beforeAll, describe, expect, test, vi } from "vitest";

describe("FilterMenu tests", () => {
	beforeAll(async () => {
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
			};
		});
	});
	test("Component can render", () => {
		const screen = render(<FilterMenu />);
		expect(
			screen.getByRole("button", { name: "New filter" }),
		).toBeInTheDocument();
	});
	test("Check a filter can be added", async () => {
		const screen = render(<FilterMenu />);

		// Click "New filter"
		const newFilterButton = screen.getByRole("button", { name: "New filter" });
		fireEvent.click(newFilterButton);

		// Open "Key" selection dropdown
		await waitFor(() => {
			fireEvent.mouseDown(screen.getByPlaceholderText("Key"));
		});

		// Select a key
		await waitFor(() => {
			fireEvent.click(screen.getByText("mocked_key1"));
		});

		// // Open "Value" selection dropdown
		fireEvent.click(screen.getByPlaceholderText("Value"));

		// Select a value
		await waitFor(() => {
			screen.getByText("mocked_key1_val1 (2)");
		});
		fireEvent.click(screen.getByText("mocked_key1_val1 (2)"));

		// // Ensure a filter appears
		expect(screen.getByText("mocked_key1: mocked_key1_val1"));
	});
});
