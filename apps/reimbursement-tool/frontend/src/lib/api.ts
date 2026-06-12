import axios from 'axios';

export const api = axios.create({
  baseURL: '/api',
  timeout: 60000,
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    const message =
      err.response?.data?.error ?? err.message ?? 'Request failed';
    return Promise.reject(new Error(message));
  }
);
