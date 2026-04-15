import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  base: "./",
  build: {
    outDir: "dist",
    emptyOutDir: true,
  },
  server: {
    port: 5174,
    proxy: {
      "/ddragon": {
        target: "https://ddragon.leagueoflegends.com",
        changeOrigin: true,
        rewrite: (path) => path.replace("/ddragon", "/cdn/14.8/img"),
      },
    },
  },
});
