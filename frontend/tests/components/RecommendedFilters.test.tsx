import { mockApi } from "@tests/apiMocks";
import { fireEvent, render, waitFor } from "@tests/testing-utils";
import RecommendedFilters from "components/RecommendedFilters";
import { beforeAll, describe, expect, test } from "vitest";

describe("RecommendedFilter tests", () => {
	beforeAll(mockApi);
	test("Component can render", () => {
		const screen = render(<RecommendedFilters />);
	});
});
