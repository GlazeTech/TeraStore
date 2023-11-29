import { KVType, PulseID } from "interfaces";

export type BackendPulseAttrValues = string[] | number[];

export interface BackendPulse {
	delays: number[];
	signal: number[];
	integration_time: number;
	creation_time: string;
	pulse_id: PulseID;
}
export interface BackendAttrKey {
	name: string;
	data_type: KVType;
}

export interface BackendTHzDevice {
	friendly_name: string;
	device_id: string;
}
