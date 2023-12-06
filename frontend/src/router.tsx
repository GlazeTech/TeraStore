import Admin from "pages/Admin";
import Home from "pages/Home";
import Register from "pages/Register";
import Signin from "pages/Signin";
import { createBrowserRouter } from "react-router-dom";

export const router = createBrowserRouter([
	{
		path: "/",
		element: <Home />,
	},
	{
		path: "/login",
		element: <Signin />,
	},
	{
		path: "/register",
		element: <Register />,
	},
	{
		path: "/admin",
		element: <Admin />,
	},
]);
