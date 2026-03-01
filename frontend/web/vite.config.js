import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    // Не проксируем /events, /auth и т.д. — иначе при перезагрузке /events запрос уходит на API и возвращается 500/JSON вместо index.html.
    // API вызывается по полному URL (http://localhost) из конфига, запросы идут на порт 80.
    historyApiFallback: true,
  },
})
