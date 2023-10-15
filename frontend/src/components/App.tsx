import { Button } from "@mui/material";
import { getPulses, pingBackend } from "api";
import "assets/App.css";
import { useState } from "react";
function App() {
	const [backendMsg, setBackendMsg] = useState<string>("");
	const [pulses, setPulses] = useState<number[]>([]);
	

	const handleButtonClick = () => {
		pingBackend().then((msg) => setBackendMsg(msg));
	};

	const handleButton2Click = () => {
		getPulses().then((data) => setPulses(data))
	};
	return (
		<div>
			<h1>Hello, world!</h1>
			<Button onClick={handleButtonClick} color="primary" variant="outlined">
				Click me
			</Button>
			<Button onClick={handleButton2Click} color="primary" variant="outlined">
				Click me
			</Button>
			<h2>{backendMsg}</h2>
			<div>{pulses}</div>
		</div>
	);
}

export default App;
