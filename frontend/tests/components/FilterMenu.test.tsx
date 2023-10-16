// import { fireEvent, render } from "@tests/testing-utils";
import { fireEvent, render } from "@tests/testing-utils";
import FilterMenu from "components/FilterMenu";
import { describe, expect, test } from "vitest";

describe("FilterMenu tests", () => {
	test("Component can render", () => {
		const screen = render(<FilterMenu />);
		expect(
			screen.getByRole("button", { name: "New filter" }),
		).toBeInTheDocument();
	});
	test("opens the 'New filter' menu when 'New filter' button is clicked", () => {
		const screen = render(<FilterMenu />);
		const newFilterButton = screen.getByRole("button", { name: "New filter" });
		fireEvent.click(newFilterButton);
		// Ensure that the menu is opened
		expect(screen.getByText("Key")).toBeInTheDocument();
	});
});

// test("Test filter menu", async () => {
// 	render(<FilterMenu />);
//     // Ensure that the component is rendered
// 	const screen = render(<FilterMenu />);
//     expect(screen.getByText("New filter")).toBeInTheDocument();

// 	// const filterBtn = screen.getByText("New filter");
// 	// screen.debug();
// 	// fireEvent.click(filterBtn);
// 	// screen.debug();
// });
