import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig(({ mode }) => {
  // 加载环境变量
  const env = loadEnv(mode, process.cwd(), '')
  const apiBaseUrl = env.VITE_API_BASE_URL || 'http://localhost:8000'
  const wsBaseUrl = env.VITE_WS_BASE_URL || 'ws://localhost:8000'
  const port = parseInt(env.VITE_PORT || '5173')

  return {
    plugins: [vue()],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url))
      }
    },
    server: {
      port,
      proxy: {
        '/api': {
          target: apiBaseUrl,
          changeOrigin: true
        },
        '/ws': {
          target: wsBaseUrl,
          ws: true
        },
        '/media': {
          target: apiBaseUrl,
          changeOrigin: true
        }
      }
    }
  }
})
