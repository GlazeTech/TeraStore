import { IAttrKey } from "interfaces";
import { useEffect, useState } from "react";
import { useFiltersStore } from "store";
import { RecommendedCard } from "./RecommendedFilterCard";

function RecommendedFilters() {
	const [notAppliedPulseKeys, pulseFilters] = useFiltersStore((state) => [
		state.notAppliedPulseKeys,
		state.pulseFilters,
	]);
	const [sortedKeys, setSortedKeys] = useState<
		{ key: IAttrKey; nPulses: number }[] | null
	>(null);

	useEffect(() => {
		if (notAppliedPulseKeys) {
			Promise.all(
				notAppliedPulseKeys.map((key) => key.getNPulsesWithKey(pulseFilters)),
			).then((pulsesPerKey) => {
				const _sorted = [...notAppliedPulseKeys]
					.map((key, idx) => ({
						key: key,
						nPulses: pulsesPerKey[idx],
					}))
					.filter((obj) => obj.nPulses > 0)
					.sort((a, b) => b.nPulses - a.nPulses);
				setSortedKeys(_sorted);
			});
		}
	}, [notAppliedPulseKeys]);

	return (
		<div style={{ display: "flex", flexWrap: "wrap" }}>
			{sortedKeys?.map((v) => (
				<RecommendedCard
					attrKey={v.key}
					nPulses={v.nPulses}
					key={`${v.key.name}-${v.key.type}`}
				/>
			))}
		</div>
	);
}

export default RecommendedFilters;
