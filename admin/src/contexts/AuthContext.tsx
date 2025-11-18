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
    // Get initial session from Supabase
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      if (session?.access_token) {
        // Store token for API service
        localStorage.setItem('admin_token', session.access_token);
        // Get user profile from API
        loadUserProfile();
      } else {
        setIsLoading(false);
      }
    });

    // Listen for auth changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(async (_event, session) => {
      setSession(session);
      if (session?.access_token) {
        localStorage.setItem('admin_token', session.access_token);
        await loadUserProfile();
      } else {
        localStorage.removeItem('admin_token');
        localStorage.removeItem('admin_user');
        setUser(null);
        setIsLoading(false);
      }
    });

    return () => subscription.unsubscribe();
  }, []);

  const loadUserProfile = async () => {
    try {
      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => reject(new Error('Request timeout')), 5000);
      });
      
      const currentUserPromise = apiService.getCurrentUser();
      const currentUser = await Promise.race([currentUserPromise, timeoutPromise]);
      setUser(currentUser);
      localStorage.setItem('admin_user', JSON.stringify(currentUser));
    } catch (error) {
      console.error('Failed to get current user:', error);
      localStorage.removeItem('admin_token');
      localStorage.removeItem('admin_user');
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (credentials: LoginCredentials): Promise<boolean> => {
    try {
      setIsLoading(true);
      
      // Use Supabase Auth for login
      const { data, error } = await supabase.auth.signInWithPassword({
        email: credentials.identifier.includes('@') 
          ? credentials.identifier 
          : await getEmailFromIdentifier(credentials.identifier),
        password: credentials.password,
      });

      if (error) throw error;

      if (data.session) {
        setSession(data.session);
        localStorage.setItem('admin_token', data.session.access_token);
        
        // Get user profile from API
        const timeoutPromise = new Promise((_, reject) => {
          setTimeout(() => reject(new Error('Request timeout')), 10000);
        });
        
        const currentUserPromise = apiService.getCurrentUser();
        const response = await Promise.race([currentUserPromise, timeoutPromise]);
        
        setUser(response);
        localStorage.setItem('admin_user', JSON.stringify(response));
        setIsLoading(false);
        return true;
      }
      
      setIsLoading(false);
      return false;
    } catch (error) {
      console.error('Login failed:', error);
      setIsLoading(false);
      return false;
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
    await supabase.auth.signOut();
    localStorage.removeItem('admin_token');
    localStorage.removeItem('admin_user');
    setUser(null);
    setSession(null);
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
