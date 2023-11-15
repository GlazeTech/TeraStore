import { getFilterResultsForEachStringValue } from "helpers";
import { IAttrKey, KVType, PulseFilter } from "interfaces";

export function attrKeyFactory(name: string, type: KVType) {
	if (type === KVType.STRING) {
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
