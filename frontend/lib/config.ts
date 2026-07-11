export const config = {
  get apiUrl() {
    const value = process.env.NEXT_PUBLIC_API_URL;
    if (!value) throw new Error('NEXT_PUBLIC_API_URL is not configured');
    return value;
  },
  get googleClientId() {
    const value = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID;
    if (!value) throw new Error('NEXT_PUBLIC_GOOGLE_CLIENT_ID is not configured');
    return value;
  },
};
