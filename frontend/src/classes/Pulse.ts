import { PulseID } from "interfaces";
import { z } from "zod";

export class Pulse {
	constructor(
		public time: number[],
		public signal: number[],
		public integrationTime: number,
		public creationTime: Date,
		public ID: PulseID,
	) {}
}

export class AnnotatedPulse {
	constructor(
		public pulse: {
			time: number[];
			signal: number[];
			signal_err: number[] | null;
		},
		public integration_time_ms: number,
		public creation_time: string,
		public device_id: number,
		public kv_pairs: { key: string; value: string | number }[],
	) {}
}

export const annotatedPulseSchema = z.object({
	pulse: z.object({
		time: z.array(z.number()),
		signal: z.array(z.number()),
		signal_err: z.array(z.number()).nullable(),
	}),
	integration_time_ms: z.number(),
	creation_time: z.string(),
	device_id: z.number(),
	kv_pairs: z.array(
		z.object({
			key: z.string(),
			value: z.union([z.string(), z.number()]),
		}),
	),
});
