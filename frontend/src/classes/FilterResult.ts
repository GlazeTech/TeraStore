import { PulseFilter, PulseMetadata } from "interfaces";

export class FilterResult {
	constructor(
		public filters: PulseFilter[],
		public pulsesMetadata: PulseMetadata[],
	) {}

	get nPulses() {
		return this.pulsesMetadata.length;
	}

	get lastFilter() {
		return this.filters[this.filters.length - 1];
	}
}
