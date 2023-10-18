import { render } from "./testing-utils";

import App from "components/App";
import { expect, test } from "vitest";

test("Simple test", () => {
	const screen = render(<App />);
	const textElement = screen.getByText("Hello, world!");
	expect(textElement).toBeInTheDocument();
});
