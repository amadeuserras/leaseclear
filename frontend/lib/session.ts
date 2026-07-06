export const TOKEN_COOKIE = 'lc_token';
export const EMAIL_COOKIE = 'lc_email';

const COOKIE_MAX_AGE_S = 60 * 60 * 24 * 7;

export const saveSession = (token: string, email: string) => {
  const attrs = `path=/; max-age=${COOKIE_MAX_AGE_S}; samesite=lax`;
  document.cookie = `${TOKEN_COOKIE}=${encodeURIComponent(token)}; ${attrs}`;
  document.cookie = `${EMAIL_COOKIE}=${encodeURIComponent(email)}; ${attrs}`;
};

export const clearSession = () => {
  document.cookie = `${TOKEN_COOKIE}=; path=/; max-age=0`;
  document.cookie = `${EMAIL_COOKIE}=; path=/; max-age=0`;
};

export const getToken = (): string | null => {
  const match = document.cookie.match(new RegExp(`(?:^|; )${TOKEN_COOKIE}=([^;]*)`));
  return match ? decodeURIComponent(match[1]) : null;
};

export const initialsFromEmail = (email: string): string => {
  const local = email.split('@')[0] ?? '';
  const parts = local.split(/[._-]+/).filter(Boolean);
  const initials = parts.length >= 2 ? `${parts[0][0]}${parts[1][0]}` : local.slice(0, 2);
  return initials.toUpperCase() || '?';
};
