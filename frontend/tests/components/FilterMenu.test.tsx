import { mockApi } from "@tests/apiMocks";
import { setupFilterStore } from "@tests/store-utils";
import { fireEvent, render, waitFor } from "@tests/testing-utils";
import FilterMenu from "components/FilterMenu";
import { beforeAll, beforeEach, describe, expect, test } from "vitest";

describe("FilterMenu tests", () => {
	beforeAll(mockApi);
	beforeEach(setupFilterStore);
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
