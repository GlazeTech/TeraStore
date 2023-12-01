import { act, renderHook } from "@testing-library/react";
import { useStoreShallow } from "store";
import { mockApi } from "./apiMocks";
// Fetch the initial state of the store
export const setupFilterStore = () => {
	mockApi();
	const func = renderHook(() =>
		useStoreShallow((state) => state.fetchInitialState),
	);
	act(() => {
		func.result.current();
	});
};
