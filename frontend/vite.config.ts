import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";

export default defineConfig({
  server: {
    host: "::",
    port: 8080,
    hmr: { overlay: false },
    proxy: {
      "/analyze-profile": "http://localhost:5000",
      "/generate-test":   "http://localhost:5000",
      "/evaluate-test":   "http://localhost:5000",
      "/compute-path":    "http://localhost:5000",
      "/chat":            "http://localhost:5000",
      "/health":          "http://localhost:5000",
    },
  },
  plugins: [react()],
  resolve: {
    alias: { "@": path.resolve(__dirname, "./src") },
  },
});
