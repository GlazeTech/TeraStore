import { render } from "./testing-utils";

import App from "components/App";
import { test } from "vitest";

test("App can render", () => {
	render(<App />);
});
