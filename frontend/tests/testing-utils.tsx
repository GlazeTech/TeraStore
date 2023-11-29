import fs from "fs";
import path from "path";
import { MantineProvider } from "@mantine/core";
import { render as testingLibraryRender } from "@testing-library/react";
import React from "react";

export * from "@testing-library/react";

export function render(ui: React.ReactNode) {
	return testingLibraryRender(<div>{ui}</div>, {
		wrapper: ({ children }: { children: React.ReactNode }) => (
			<MantineProvider>{children}</MantineProvider>
		),
	});
}

export function readTestingAsset(name: string) {
	const testsFolder = path.resolve(__dirname);
	return fs.readFileSync(
		path.join(testsFolder, "testing-assets", name),
		"utf-8",
	);
}
