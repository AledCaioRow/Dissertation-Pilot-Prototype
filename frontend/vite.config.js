import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// The backend runs on :8000. All API calls are made to `/api/*` and proxied here,
// with the `/api` prefix stripped, so the frontend code stays origin-agnostic.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
});
