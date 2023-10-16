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
