export interface PulseFilter {
	key: string;
	value: string;
}

export interface PulseFromBackend {
	delays: number[];
	signal: number[];
	integration_time: number;
	creation_time: string;
	pulse_id: string;
}
