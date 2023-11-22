import { BackendTHzDevice, PulseID } from "interfaces";
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
			signal_err?: number[] | null;
		},
		public integration_time_ms: number,
		public creation_time: Date,
		public device_id: number,
		public pulse_attributes: { key: string; value: string | number }[],
	) {}

	static validateAndParse(
		data: unknown,
		devices: BackendTHzDevice[],
	): AnnotatedPulse {
		let parsed: z.infer<typeof annotatedPulseSchema>;
		try {
			parsed = annotatedPulseSchema.parse(data);
		} catch {
			throw new AnnotatedPulseParsingError("Failed to parse AnnotatedPulse");
		}

		const creationTime = new Date(parsed.creation_time);
		if (isNaN(creationTime.getTime())) {
			throw new InvalidCreationTimeError(
				`Failed to parse creation_time: ${parsed.creation_time}`,
			);
		}

		const deviceIdIsValid = devices.some(
			(device) => device.device_id === parsed.device_id,
		);
		if (!deviceIdIsValid) {
			throw new InvalidDeviceIDError(
				`Device ID ${parsed.device_id} does not exist.`,
			);
		}

		return new AnnotatedPulse(
			{
				time: parsed.pulse.time,
				signal: parsed.pulse.signal,
				signal_err: parsed.pulse.signal_err,
			},
			parsed.integration_time_ms,
			creationTime,
			parsed.device_id,
			parsed.pulse_attributes,
		);
	}
}

const annotatedPulseSchema = z.object({
	pulse: z.object({
		time: z.array(z.number()),
		signal: z.array(z.number()),
		signal_err: z.optional(z.array(z.number()).nullable()),
	}),
	integration_time_ms: z.number(),
	creation_time: z.string(),
	device_id: z.number(),
	pulse_attributes: z.array(
		z.object({
			key: z.string(),
			value: z.union([z.string(), z.number()]),
		}),
	),
});

export class AnnotatedPulseParsingError extends Error {
	constructor(message: string) {
		super(message);
		this.name = "ParseError";
	}
}

export class InvalidDeviceIDError extends Error {
	constructor(message: string) {
		super(message);
		this.name = "InvalidDeviceIDError";
	}
}

export class InvalidCreationTimeError extends Error {
	constructor(message: string) {
		super(message);
		this.name = "InvalidCreationTimeError";
	}
}
