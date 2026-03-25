import tailwindcss from '@tailwindcss/vite';
import react from '@vitejs/plugin-react';
import path from 'path';
import {defineConfig, loadEnv} from 'vite';

export default defineConfig(({mode}) => {
  const env = loadEnv(mode, '.', '');
  return {
    plugins: [react(), tailwindcss()],
    define: {
      'process.env.GEMINI_API_KEY': JSON.stringify(env.GEMINI_API_KEY),
    },
    resolve: {
      alias: {
        '@': path.resolve(__dirname, '.'),
      },
    },
    server: {
      hmr: process.env.DISABLE_HMR !== 'true',
      watch: {
        // O SEGREDO ESTÁ AQUI: O Vite fica cego para a Base de Dados e Logs
        ignored:[
          '**/*.log', 
          '**/vagas_vistas.json', 
          '**/kanban_state.json', 
          '**/todo_list.json'
        ]
      }
    },
  };
});
