import { mockApi } from "@tests/apiMocks";
import { render } from "@tests/testing-utils";
import RecommendedFilters from "components/RecommendedFilters";
import { beforeAll, describe, test } from "vitest";

describe("RecommendedFilter tests", () => {
	beforeAll(mockApi);
	test("Component can render", () => {
		render(<RecommendedFilters />);
	});
});
