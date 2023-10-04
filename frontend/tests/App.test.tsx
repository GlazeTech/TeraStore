import { render } from "@testing-library/react";
import React from "react";
import { expect, test } from "vitest";
import App from "../src/components/App";

test("Simple test", () => {
	const screen = render(<App />);
	const textElement = screen.getByText("Hello, world!");
	expect(textElement).toBeInTheDocument();
});
