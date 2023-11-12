import { ReactNode } from "react";

export interface SliderMark {
	value: number;
	label?: ReactNode;
}

export interface Option {
	value: string;
	label: string;
}
