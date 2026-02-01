import { useState, useEffect, useCallback } from 'react';
import { onAuthStateChanged, signInWithGoogle, signOut, getCurrentUser } from '../services/auth';
import { registerUser } from '../services/api';
import type { User } from '../types';

export function useAuth() {
  const [user, setUser] = useState<User | null>(getCurrentUser());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged((user) => {
      setUser(user);
      setLoading(false);
    });
    return unsubscribe;
  }, []);

  const login = useCallback(async () => {
    setError(null);
    setLoading(true);
    try {
      const user = await signInWithGoogle();
      await registerUser({
        id: user.id,
        email: user.email,
        name: user.name,
      });
      setUser(user);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
    } finally {
      setLoading(false);
    }
  }, []);

  const logout = useCallback(async () => {
    setError(null);
    try {
      await signOut();
      setUser(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Logout failed');
    }
  }, []);

  return {
    user,
    loading,
    error,
    login,
    logout,
    isAuthenticated: !!user,
  };
}
