import { getFilteredPulses, getKeyValues } from "api";
import { getFilterResultsForEachStringValue } from "helpers";
import { IAttrKey, KVType, PulseFilter } from "interfaces";
import { PulseNumberFilter } from "./PulseFilter";

export function attrKeyFactory(name: string, type: KVType) {
	if (type === KVType.NUMBER) {
		return new NumberAttrKey(name);
	} else if (type === KVType.STRING) {
		return new StringAttrKey(name);
	} else {
		throw new Error("Unhandled pulse attribute key type");
	}
}

class BaseAttrKey {
	constructor(public readonly name: string, public readonly type: KVType) {}

	isEqualTo(key: IAttrKey): boolean {
		return key.name === this.name && key.type === this.type;
	}
}

export class StringAttrKey extends BaseAttrKey implements IAttrKey {
	constructor(readonly name: string) {
		super(name, KVType.STRING);
	}

	async getNPulsesWithKey(additionalFilters: PulseFilter[]): Promise<number> {
		return getFilterResultsForEachStringValue(this, additionalFilters).then(
			(filters) => filters.reduce((sum, current) => sum + current.nPulses, 0),
		);
	}
}

export class NumberAttrKey extends BaseAttrKey implements IAttrKey {
	constructor(readonly name: string) {
		super(name, KVType.NUMBER);
	}

	async getNPulsesWithKey(additionalFilters: PulseFilter[]): Promise<number> {
		const keyValues = await getKeyValues<number[]>(this);

		const filterResult = await getFilteredPulses([
			...additionalFilters,
			new PulseNumberFilter(
				this,
				Math.min(...keyValues),
				Math.max(...keyValues),
			),
		]);
		return filterResult.nPulses;
	}
}
