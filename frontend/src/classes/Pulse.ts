import { PulseID } from "interfaces";

export class Pulse {
	constructor(
		public time: number[],
		public signal: number[],
		public integrationTime: number,
		public creationTime: Date,
		public ID: PulseID,
	) {}
}
