// import { fireEvent, render } from "@tests/testing-utils";
import { fireEvent, render } from "@tests/testing-utils";
import FilterMenu from "components/FilterMenu";
import { expect, test } from "vitest";

test("Test filter menu", async () => {
	const screen = render(<FilterMenu />);
	const filterBtn = screen.getByText("New filter");
	screen.debug();
	fireEvent.click(filterBtn);
	screen.debug();
});
