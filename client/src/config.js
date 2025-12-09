
const getApiUrl = () => {
    // Get the env var
    let url = import.meta.env.VITE_API_URL;

    // If not set, default to localhost (development fallback)
    if (!url) {
        // If we are in production (based on mode or hostname), this might be wrong if env var is missed.
        // But for now, keep localhost default for local dev.
        return 'http://localhost:10000';
    }

    // If protocol is missing (Render provided just the host), prepend https://
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
        url = `https://${url}`;
    }

    // Remove trailing slash
    return url.replace(/\/$/, '');
};

export const API_URL = getApiUrl();
