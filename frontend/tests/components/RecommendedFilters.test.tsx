import { render } from "@tests/testing-utils";
import RecommendedFilters from "components/RecommendedFilters";
import { describe, test } from "vitest";

describe("RecommendedFilter tests", () => {
	test("Component can render", () => {
		render(<RecommendedFilters />);
	});
});
