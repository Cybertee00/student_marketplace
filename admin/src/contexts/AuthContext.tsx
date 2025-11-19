import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User, LoginCredentials } from '@/types';
import { apiService } from '@/services/api';
import { supabase } from '@/services/supabase';
import type { Session } from '@supabase/supabase-js';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  login: (credentials: LoginCredentials) => Promise<boolean>;
  logout: () => void;
  isAuthenticated: boolean;
  session: Session | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let mounted = true;

    const bootstrap = async () => {
      setIsLoading(true);
      try {
        const { data, error } = await supabase.auth.getSession();
        if (!mounted) return;

        if (error) {
          throw error;
        }

        const activeSession = data.session;
        if (!activeSession) {
          localStorage.removeItem('admin_token');
          localStorage.removeItem('admin_user');
          setSession(null);
          setUser(null);
          return;
        }

        await loadUserProfile(activeSession);
      } catch (error) {
        console.warn('Failed to bootstrap session', error);
        if (mounted) {
          await clearAuthState();
        }
      } finally {
        if (mounted) {
          setIsLoading(false);
        }
      }
    };

    bootstrap();

    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (_event, session) => {
        if (!mounted) {
          return;
        }

        if (!session) {
          await clearAuthState();
          setIsLoading(false);
          return;
        }

        setIsLoading(true);
        try {
          await loadUserProfile(session);
        } catch (error) {
          console.error('Auth state change handling failed:', error);
          await clearAuthState();
        } finally {
          if (mounted) {
            setIsLoading(false);
          }
        }
      }
    );

    return () => {
      mounted = false;
      subscription.unsubscribe();
    };
  }, []);

  const clearAuthState = async () => {
    try {
      await supabase.auth.signOut();
    } catch (error) {
      console.error('Error clearing Supabase session:', error);
    } finally {
      localStorage.removeItem('admin_token');
      localStorage.removeItem('admin_user');
      setUser(null);
      setSession(null);
      setIsLoading(false);
    }
  };

  const loadUserProfile = async (session: Session) => {
    if (!session?.access_token || !session.user) {
      throw new Error('No active session');
    }

    const profilePromise = apiService.getCurrentUser();
    const timeoutPromise = new Promise<never>((_, reject) =>
      setTimeout(() => reject(new Error('Profile request timed out')), 8000)
    );

    const currentUser = await Promise.race([profilePromise, timeoutPromise]);

    setSession(session);
    setUser(currentUser);
    localStorage.setItem('admin_token', session.access_token);
    localStorage.setItem('admin_user', JSON.stringify(currentUser));

    return currentUser;
  };

  const login = async (credentials: LoginCredentials): Promise<boolean> => {
    setIsLoading(true);
    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email: credentials.identifier.includes('@')
          ? credentials.identifier
          : await getEmailFromIdentifier(credentials.identifier),
        password: credentials.password,
      });

      if (error || !data.session) {
        throw error || new Error('Unable to start session');
      }

      await loadUserProfile(data.session);
      return true;
    } catch (error) {
      console.error('Login failed:', error);
      await clearAuthState();
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const getEmailFromIdentifier = async (identifier: string): Promise<string> => {
    // Try to get email from profiles table
    const { data, error } = await supabase
      .from('profiles')
      .select('email')
      .or(`username.eq.${identifier},phone.eq.${identifier}`)
      .single();
    
    if (error || !data) {
      throw new Error('Invalid credentials');
    }
    
    return data.email;
  };

  const logout = async () => {
    await clearAuthState();
  };

  const isAuthenticated = !!user && !!session;
  
  const value: AuthContextType = {
    user,
    isLoading,
    login,
    logout,
    isAuthenticated,
    session,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
