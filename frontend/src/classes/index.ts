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
