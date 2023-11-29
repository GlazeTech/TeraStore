import { getPulseKeys } from "api";
import { DateAttrKey } from "classes";
import { produce } from "immer";
import { IAttrKey, PulseFilter } from "interfaces";
import { create } from "zustand";

interface filtersStore {
	notAppliedPulseKeys: IAttrKey[] | undefined;
	setNotAppliedPulseKeys: (keys: IAttrKey[]) => void;
	pulseFilters: PulseFilter[];
	addPulseFilter: (filter: PulseFilter) => void;
	removePulseFilter: (filter: PulseFilter) => void;
	fetchInitialState: () => Promise<void>;
}

export const useFiltersStore = create<filtersStore>()((set, get) => ({
	notAppliedPulseKeys: undefined,
	setNotAppliedPulseKeys: (keys) =>
		set(produce((_state) => ({ notAppliedPulseKeys: keys }))),

	pulseFilters: [],
	addPulseFilter: (filter) => {
		const filters = [...get().pulseFilters, filter];
		const keys = get().notAppliedPulseKeys?.filter(
			(key) => !key.isEqualTo(filter.key),
		);
		set(
			produce((_state) => ({
				pulseFilters: filters,
				notAppliedPulseKeys: keys,
			})),
		);
	},
	removePulseFilter: (filterToDelete) => {
		const filters = get().pulseFilters.filter(
			(filter) => filter !== filterToDelete,
		);
		const keys = get().notAppliedPulseKeys;
		if (keys) {
			set(
				produce((_state) => ({
					pulseFilters: filters,
					notAppliedPulseKeys: [...keys, filterToDelete.key],
				})),
			);
		} else {
			throw new Error("Expected notAppliedPulseKeys to be defined");
		}
	},

	fetchInitialState: async () => {
		getPulseKeys().then((keys) => {
			set({ notAppliedPulseKeys: [...keys, new DateAttrKey("date")] });
		});
	},
}));
