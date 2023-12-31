import { KVType, PulseID } from "interfaces";

export interface BackendPulseAttr {
	key: string;
	value: string | number;
}

export interface BackendPulse {
	delays: number[];
	signal: number[];
	signal_error: number[] | null;
	integration_time_ms: number;
	creation_time: string;
	pulse_id: PulseID;
	device_id: string;
	pulse_attributes: BackendPulseAttr[];
}
export interface BackendAttrKey {
	name: string;
	data_type: KVType;
}

export interface BackendTHzDevice {
	friendly_name: string;
	device_id: string;
}
