import { IAttrKey, IPulseFilterString } from "interfaces";


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
			data_type: "string",
		};
	}
}
