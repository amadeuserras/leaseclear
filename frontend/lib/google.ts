const GIS_SCRIPT_SRC = 'https://accounts.google.com/gsi/client';

type GoogleTokenClient = {
  requestAccessToken: () => void;
};

type GoogleTokenResponse = {
  access_token?: string;
  error?: string;
};

type GoogleAccounts = {
  accounts: {
    oauth2: {
      initTokenClient: (config: {
        client_id: string;
        scope: string;
        callback: (response: GoogleTokenResponse) => void;
        error_callback?: () => void;
      }) => GoogleTokenClient;
    };
  };
};

declare global {
  interface Window {
    google?: GoogleAccounts;
  }
}

let scriptPromise: Promise<void> | null = null;

const loadGis = (): Promise<void> => {
  if (window.google?.accounts?.oauth2) return Promise.resolve();
  if (scriptPromise) return scriptPromise;
  scriptPromise = new Promise((resolve, reject) => {
    const existing = document.querySelector<HTMLScriptElement>(`script[src="${GIS_SCRIPT_SRC}"]`);
    if (existing) {
      existing.addEventListener('load', () => resolve());
      existing.addEventListener('error', () => reject(new Error('Failed to load Google sign-in')));
      return;
    }
    const script = document.createElement('script');
    script.src = GIS_SCRIPT_SRC;
    script.async = true;
    script.onload = () => resolve();
    script.onerror = () => reject(new Error('Failed to load Google sign-in'));
    document.head.appendChild(script);
  });
  return scriptPromise;
};

export const requestGoogleAccessToken = async (): Promise<string> => {
  const clientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID;
  if (!clientId) throw new Error('Google sign-in is not configured');

  await loadGis();
  if (!window.google?.accounts?.oauth2) {
    throw new Error('Google sign-in is unavailable');
  }

  return new Promise((resolve, reject) => {
    const client = window.google!.accounts.oauth2.initTokenClient({
      client_id: clientId,
      scope: 'openid email profile',
      callback: (response) => {
        if (response.error || !response.access_token) {
          reject(new Error(response.error || 'Google sign-in failed'));
          return;
        }
        resolve(response.access_token);
      },
      error_callback: () => reject(new Error('Google sign-in was cancelled')),
    });
    client.requestAccessToken();
  });
};
