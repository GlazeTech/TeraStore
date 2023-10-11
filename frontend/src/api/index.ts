import axios from "axios";

const api = axios.create({
  baseURL: "http://0.0.0.0:8000",
});

export async function pingBackend(): Promise<string> {
  return api.get("/").then((resp) => {
    return resp.data.message;
  });
}
