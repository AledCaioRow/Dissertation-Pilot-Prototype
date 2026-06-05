import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// In dev, proxy /api/* to the FastAPI backend so the frontend can use relative
// URLs (no CORS, no hard-coded port). Override the target with BACKEND_URL.
const BACKEND = process.env.BACKEND_URL || "http://localhost:8000";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": { target: BACKEND, changeOrigin: true },
    },
  },
});
