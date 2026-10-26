import { create } from 'zustand';
import api from '../services/api';

interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  is_superuser: boolean;
  organization_id: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  loading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (data: {
    organization_name: string;
    user_email: string;
    password: string;
    first_name: string;
    last_name: string;
  }) => Promise<void>;
  logout: () => void;
  fetchMe: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: localStorage.getItem('nexora_token'),
  loading: false,
  error: null,

  login: async (email, password) => {
    set({ loading: true, error: null });
    try {
      const { data } = await api.post('/auth/login', {
        email,
        password,
      });
      localStorage.setItem('nexora_token', data.access_token);
      set({ token: data.access_token });
      const me = await api.get('/auth/me');
      set({ user: me.data, loading: false });
    } catch (e: any) {
      set({ loading: false, error: e.response?.data?.detail || 'Login failed' });
      throw e;
    }
  },

  register: async (data) => {
    set({ loading: true, error: null });
    try {
      const res = await api.post('/auth/register', data);
      localStorage.setItem('nexora_token', res.data.access_token);
      set({ token: res.data.access_token });
      const me = await api.get('/auth/me');
      set({ user: me.data, loading: false });
    } catch (e: any) {
      set({ loading: false, error: e.response?.data?.detail || 'Registration failed' });
      throw e;
    }
  },

  logout: () => {
    localStorage.removeItem('nexora_token');
    set({ user: null, token: null });
  },

  fetchMe: async () => {
    try {
      const { data } = await api.get('/auth/me');
      set({ user: data });
    } catch {
      localStorage.removeItem('nexora_token');
      set({ user: null, token: null });
    }
  },
}));
