import { act, renderHook } from "@testing-library/react";
import { useStoreShallow } from "store";

// Fetch the initial state of the store
export const setupFilterStore = () => {
	const func = renderHook(() =>
		useStoreShallow((state) => state.fetchInitialState),
	);
	act(() => {
		func.result.current();
	});
};
