import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig(({ mode }) => {
  // 加载环境变量
  const env = loadEnv(mode, process.cwd(), '')
  
  // 验证必需的环境变量
  const apiBaseUrl = env.VITE_API_BASE_URL
  if (!apiBaseUrl) {
    throw new Error('VITE_API_BASE_URL 环境变量未设置，请在 .env 文件中配置')
  }
  
  const wsBaseUrl = env.VITE_WS_BASE_URL
  if (!wsBaseUrl) {
    throw new Error('VITE_WS_BASE_URL 环境变量未设置，请在 .env 文件中配置')
  }
  
  // 可选配置项可设置默认值
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
