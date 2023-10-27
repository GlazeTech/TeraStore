import { render } from "./testing-utils";

import { mockApi } from "@tests/apiMocks";
import App from "components/App";
import { beforeAll, describe, test } from "vitest";
describe("App tests", () => {
	beforeAll(mockApi);
	test("App can render", () => {
		render(<App />);
	});
});
