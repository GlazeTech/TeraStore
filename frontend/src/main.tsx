import { MantineProvider } from "@mantine/core";
import "@mantine/core/styles.css";
import "@mantine/dates/styles.css";
import "@mantine/dropzone/styles.css";
import { Notifications } from "@mantine/notifications";
import "@mantine/notifications/styles.css";
import React from "react";
import ReactDOM from "react-dom/client";
import { RouterProvider } from "react-router-dom";
import { router } from "router";

const root = ReactDOM.createRoot(document.getElementById("root") as Element);

root.render(
	<React.StrictMode>
		<MantineProvider defaultColorScheme="auto">
			<Notifications position="top-right" />
			<RouterProvider router={router} />
		</MantineProvider>
	</React.StrictMode>,
);
