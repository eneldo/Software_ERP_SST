import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");

  return {
    plugins: [react()],

    server: {
      host: env.VITE_DEV_HOST || "127.0.0.1",
      port: Number(env.VITE_DEV_PORT || 5173),
      strictPort: true
    },

    preview: {
      host: env.VITE_PREVIEW_HOST || "127.0.0.1",
      port: Number(env.VITE_PREVIEW_PORT || 4173),
      strictPort: true
    },

    build: {
      target: "es2020",
      outDir: "dist",
      assetsDir: "assets",
      sourcemap: false,
      minify: "esbuild",
      cssCodeSplit: true,
      chunkSizeWarningLimit: 1200,
      rollupOptions: {
        output: {
          manualChunks: {
            react: ["react", "react-dom", "react-router-dom"],
            charts: ["recharts"],
            icons: ["lucide-react"],
            http: ["axios"]
          }
        }
      }
    }
  };
});
