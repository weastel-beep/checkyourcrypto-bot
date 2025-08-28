import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [
    vue(),
    {
      name: 'html-transform',
      transformIndexHtml(html) {
        return html.replace(
          /<script type="module" crossorigin src="([^"]+)"/g,
          '<script type="module" crossorigin src="$1?v=' + Date.now() + '"'
        ).replace(
          /<link rel="stylesheet" crossorigin href="([^"]+)"/g,
          '<link rel="stylesheet" crossorigin href="$1?v=' + Date.now() + '"'
        );
      }
    }
  ],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    rollupOptions: {
      output: {
        entryFileNames: `assets/[name]-[hash].js`,
        chunkFileNames: `assets/[name]-[hash].js`,
        assetFileNames: `assets/[name]-[hash].[ext]`
      }
    }
  },
  define: {
    __VUE_OPTIONS_API__: true,
    __VUE_PROD_DEVTOOLS__: false,
  }
})
