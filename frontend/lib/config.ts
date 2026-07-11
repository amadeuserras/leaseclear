const requireEnv = (name: string): string => {
  const value = process.env[name];
  if (!value) throw new Error(`${name} is not configured`);
  return value;
};

export const config = {
  get backendUrl() {
    return requireEnv('NEXT_PUBLIC_BACKEND_URL');
  },
  get googleClientId() {
    return requireEnv('NEXT_PUBLIC_GOOGLE_CLIENT_ID');
  },
};
