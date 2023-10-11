import { Button } from "@mui/material";
import { pingBackend } from "api";
import "assets/App.css";
import { useState } from "react";
function App() {
	const [backendMsg, setBackendMsg] = useState<string>("");

	const handleButtonClick = () => {
		pingBackend().then((msg) => setBackendMsg(msg));
	};

	return (
		<div>
			<h1>Hello, world!</h1>
			<Button onClick={handleButtonClick} color="primary" variant="outlined">
				Click me
			</Button>
			<h2>{backendMsg}</h2>
		</div>
	);
}

export default App;
