import {
	IAttrKey,
	IPulseFilterDate,
	IPulseFilterNumber,
	IPulseFilterString,
} from "interfaces";

export class PulseNumberFilter implements IPulseFilterNumber {
	constructor(
		public key: IAttrKey,
		public lower: number,
		public upper: number,
	) {}

	hash(): string {
		return `${this.key.name}:${this.lower}-${this.upper}`;
	}
	displayFilter(): string {
		return `${this.key.name}: ${this.lower}-${this.upper}`;
	}

	displayValue(): string {
		return `${this.lower}-${this.upper}`;
	}

	asBackendFilter(): object {
		return {
			key: this.key.name,
			min_value: this.lower,
			max_value: this.upper,
		};
	}
}

export class PulseStringFilter implements IPulseFilterString {
	constructor(public key: IAttrKey, public value: string) {}

	hash(): string {
		return `${this.key.name}:${this.value}`;
	}

	displayFilter(): string {
		return `${this.key.name}: ${this.value}`;
	}

	displayValue(): string {
		return this.value;
	}

	asBackendFilter(): object {
		return {
			key: this.key.name,
			value: this.value,
		};
	}
}

export class PulseDateFilter implements IPulseFilterDate {
	constructor(public key: IAttrKey, public lower: Date, public upper: Date) {}

	hash(): string {
		return `${
			this.key.name
		}:${this.lower.toISOString()}-${this.upper.toISOString()}`;
	}

	displayFilter(): string {
		return `${this.key.name}: ${this.formattedDates()}`;
	}

	displayValue(): string {
		return this.formattedDates();
	}

	asBackendFilter(): object {
		return {
			key: this.key.name,
			min_value: this.lower.toISOString(),
			max_value: this.upper.toISOString(),
		};
	}

	private formattedDates(): string {
		const lowerFormatted = `${this.lower.getFullYear()}/${
			this.lower.getMonth() + 1
		}/${this.lower.getDate()}`;
		const upperFormatted = `${this.upper.getFullYear()}/${
			this.upper.getMonth() + 1
		}/${this.upper.getDate()}`;
		return `${lowerFormatted} - ${upperFormatted}`;
	}
}
