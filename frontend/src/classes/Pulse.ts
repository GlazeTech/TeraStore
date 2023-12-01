import { BackendPulse, BackendTHzDevice } from "interfaces";
import { z } from "zod";

export class AnnotatedPulse {
	constructor(
		public pulse: {
			time: number[];
			signal: number[];
			signal_err: number[] | null;
		},
		public integration_time_ms: number,
		public creation_time: Date,
		public device_id: string,
		public pulse_attributes: { key: string; value: string | number }[],
		public pulse_id?: string,
	) {}

	static fromBackendPulse(pulse: BackendPulse): AnnotatedPulse {
		return new AnnotatedPulse(
			{
				time: pulse.delays,
				signal: pulse.signal,
				signal_err: pulse.signal_error,
			},
			pulse.integration_time_ms,
			new Date(pulse.creation_time),
			pulse.device_id,
			pulse.pulse_attributes,
			pulse.pulse_id,
		);
	}

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

	static pulseAttrAsBackendCompatible(key: string, value: string | number) {
		const dataType = typeof value === "string" ? "string" : "float";
		return {
			key: key,
			value: value,
			data_type: dataType,
		};
	}

	asBackendCompatible() {
		return {
			delays: this.pulse.time,
			signal: this.pulse.signal,
			integration_time_ms: this.integration_time_ms,
			creation_time: this.creation_time.toISOString(),
			device_id: this.device_id,
			pulse_attributes: this.pulse_attributes.map((attr) =>
				AnnotatedPulse.pulseAttrAsBackendCompatible(attr.key, attr.value),
			),
		};
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
	device_id: z.string(),
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
