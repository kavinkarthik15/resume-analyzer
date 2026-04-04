import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import svgr from 'vite-plugin-svgr'
// order: svgr before react so svg imports are transformed first

export default defineConfig({
  plugins: [
    svgr(),
    react(),
    tailwindcss(),
  ],
})
