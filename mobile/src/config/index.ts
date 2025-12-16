// Use environment variable for production, fallback to localhost for development
const API_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000';

export const config = {
  apiUrl: API_URL,
};
