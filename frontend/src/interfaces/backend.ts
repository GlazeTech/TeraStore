export interface BackendPulse {
	delays: number[];
	signal: number[];
	integration_time: number;
	creation_time: string;
	pulse_id: number;
}

export type BackendAttrKey = string;
export type BackendPulseAttrValues = string[] | number[];
