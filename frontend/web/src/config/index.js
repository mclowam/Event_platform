/**
 * API base URL. Пусто = запросы относительно текущего хоста (когда фронт за nginx на :80).
 * Иначе задать VITE_API_URL в .env (напр. http://localhost для dev с порта 3000).
 */
export const API_BASE_URL = import.meta.env.VITE_API_URL ?? '';

export const ROLES = {
  volunteer: 'volunteer',
  organizer: 'organizer',
  admin: 'admin',
};

export const STORAGE_KEYS = {
  authTokens: 'authTokens',
};
