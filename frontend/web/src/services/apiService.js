const API_BASE_URL = 'http://localhost/'

export function clearTokens() {
    localStorage.removeItem('authTokens');
}

export function setTokens(tokens) {
    if (tokens) {
        localStorage.setItem('authTokens', JSON.stringify(tokens));
    } else {
        localStorage.removeItem('authTokens');
    }
}

export function loadTokensFromStorage() {
    try {
        const raw = localStorage.getItem('authTokens');
        if (!raw) return null;
        return JSON.parse(raw);
    } catch {
        return null;
    }
}

export async function apiRequest(path, options = {}) {
    const { method = 'GET', body, headers = {} } = options;

    const tokens = loadTokensFromStorage();
    const accessToken = tokens?.access;

    const finalHeaders = {
        'Content-Type': 'application/json',
        ...headers,
    };

    if (accessToken) {
        finalHeaders.Authorization = `Bearer ${accessToken}`;
    }

    const res = await fetch(API_BASE_URL + path, {
        method,
        headers: finalHeaders,
        body: body ? JSON.stringify(body) : undefined,
    });

    const text = await res.text();
    let data;
    try {
        data = text ? JSON.parse(text) : null;
    } catch {
        data = text;
    }

    if (!res.ok) {
        const error = new Error('API error');
        error.status = res.status;
        error.data = data;
        throw error;
    }

    return data;
}