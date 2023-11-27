export * from "./backend";
export * from "./mantine";

export enum KVType {
	NUMBER = "float",
	STRING = "string",
}
export interface IAttrKey {
	name: string;
	type: KVType;
	getNPulsesWithKey(additionalFilters: PulseFilter[]): Promise<number>;
	isEqualTo(key: IAttrKey): boolean;
}

interface PulseFilterBase {
	key: IAttrKey;
	hash(): string;
	displayFilter(): string;
	displayValue(): string;
	asBackendFilter(): object;
}

export interface IPulseFilterString extends PulseFilterBase {
	value: string;
}

export interface IPulseFilterNumber extends PulseFilterBase {
	lower: number;
	upper: number;
}

export type PulseFilter = IPulseFilterString | IPulseFilterNumber;

export type PulseID = number;