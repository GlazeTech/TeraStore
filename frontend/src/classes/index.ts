import { PulseFilter } from "interfaces";

export class FilterResult {
	constructor(public filters: PulseFilter[], public pulseIDs: string[]) {}

	get nPulses() {
		return this.pulseIDs.length;
	}

	get lastFilter() {
		return this.filters[this.filters.length - 1];
	}
}

export class Pulse {
	constructor(
		public time: number[],
		public signal: number[],
		public integrationTime: number,
		public creationTime: Date,
		public ID: string,
	) {}
}
