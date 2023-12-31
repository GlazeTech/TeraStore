export * from "./backend";
export * from "./mantine";
export * from "./auth";

export enum KVType {
	NUMBER = "float",
	STRING = "string",
	DATE = "date",
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

export interface IPulseFilterDate extends PulseFilterBase {
	lower: Date;
	upper: Date;
}

export interface PulseMetadata {
	pulseID: PulseID;
	creationTime: Date;
}

export type PulseFilter =
	| IPulseFilterString
	| IPulseFilterNumber
	| IPulseFilterDate;

export type PulseID = string;
