import { render } from "./testing-utils";

import App from "components/App";
import { describe, test } from "vitest";
describe("App tests", () => {
	test("App can render", () => {
		render(<App />);
	});
});
