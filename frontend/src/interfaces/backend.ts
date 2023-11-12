import { KVType } from "interfaces";

export interface BackendPulse {
	delays: number[];
	signal: number[];
	integration_time: number;
	creation_time: string;
	pulse_id: number;
}
export interface BackendAttrKey {
	name: string;
	data_type: KVType;
}
export type BackendPulseAttrValues = string[] | number[];
