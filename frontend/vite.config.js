import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// `npm run dev` proxies the API through the docker compose stack on :6780.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 6773,
    proxy: { "/api": "http://localhost:6780" },
  },
});
