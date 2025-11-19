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

    const initSession = async () => {
      try {
        const { data: { session } } = await supabase.auth.getSession();

        if (!mounted) return;

        setSession(session);
        if (session?.access_token && session?.user?.id) {
          localStorage.setItem('admin_token', session.access_token);
          loadUserProfile();
        } else {
          localStorage.removeItem('admin_token');
          localStorage.removeItem('admin_user');
          setUser(null);
          setIsLoading(false);
        }
      } catch (error) {
        console.error('Error getting session:', error);
        if (!mounted) return;

        localStorage.removeItem('admin_token');
        localStorage.removeItem('admin_user');
        setUser(null);
        setSession(null);
        setIsLoading(false);
      }
    };

    initSession();

    // Listen for auth changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(async (_event, session) => {
      if (!mounted) return;
      
      setSession(session);
      if (session?.access_token && session?.user?.id) {
        localStorage.setItem('admin_token', session.access_token);
        await loadUserProfile();
      } else {
        localStorage.removeItem('admin_token');
        localStorage.removeItem('admin_user');
        setUser(null);
        setIsLoading(false);
      }
    });

    return () => {
      mounted = false;
      subscription.unsubscribe();
    };
  }, []);

  const loadUserProfile = async () => {
    try {
      setIsLoading(true);
      
      // First, try to get from Supabase directly (faster and more reliable)
      const { data: { session } } = await supabase.auth.getSession();
      if (!session?.user?.id) {
        throw new Error('No session found');
      }

      const profileResponse = await supabase
        .from('profiles')
        .select('*')
        .eq('id', session.user.id)
        .single();

      if (profileResponse.data) {
        // Map Supabase profile to User type
        const userFromSupabase = {
          id: profileResponse.data.id,
          name: profileResponse.data.name,
          surname: profileResponse.data.surname,
          email: profileResponse.data.email,
          phone: profileResponse.data.phone,
          username: profileResponse.data.username,
          profile_img: profileResponse.data.profile_img,
          created_at: profileResponse.data.created_at,
          is_email_verified: profileResponse.data.is_email_verified || false,
          is_phone_verified: profileResponse.data.is_phone_verified || false,
        };
        
        setUser(userFromSupabase);
        localStorage.setItem('admin_user', JSON.stringify(userFromSupabase));
        setIsLoading(false);
        return;
      }

      // Fallback: Try API (but don't wait too long)
      try {
        const timeoutPromise = new Promise((_, reject) => {
          setTimeout(() => reject(new Error('Request timeout')), 3000);
        });
        
        const currentUserPromise = apiService.getCurrentUser();
        const currentUser = await Promise.race([currentUserPromise, timeoutPromise]);
        setUser(currentUser);
        localStorage.setItem('admin_user', JSON.stringify(currentUser));
      } catch (apiError) {
        console.warn('API call failed, using Supabase profile:', apiError);
        // Already set user from Supabase above, so this is fine
      }
    } catch (error) {
      console.error('Failed to get user profile:', error);
      // Don't clear tokens on error - user might still be valid
      // Only clear if it's a clear auth error
      if (error instanceof Error && error.message.includes('401') || error.message.includes('Unauthorized')) {
        localStorage.removeItem('admin_token');
        localStorage.removeItem('admin_user');
        setUser(null);
      }
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
        try {
          const timeoutPromise = new Promise((_, reject) => {
            setTimeout(() => reject(new Error('Request timeout')), 10000);
          });
          
          const currentUserPromise = apiService.getCurrentUser();
          const response = await Promise.race([currentUserPromise, timeoutPromise]);
          
          setUser(response);
          localStorage.setItem('admin_user', JSON.stringify(response));
          setIsLoading(false);
          return true;
        } catch (profileError) {
          console.error('Failed to get user profile from API:', profileError);
          // If profile fetch fails, try to get from Supabase directly
          try {
            const profileResponse = await supabase
              .from('profiles')
              .select('*')
              .eq('id', data.session.user.id)
              .single();
            
            if (profileResponse.data) {
              // Map Supabase profile to User type
              const userFromSupabase = {
                id: profileResponse.data.id,
                name: profileResponse.data.name,
                surname: profileResponse.data.surname,
                email: profileResponse.data.email,
                phone: profileResponse.data.phone,
                username: profileResponse.data.username,
                profile_img: profileResponse.data.profile_img,
                created_at: profileResponse.data.created_at,
                is_email_verified: profileResponse.data.is_email_verified || false,
                is_phone_verified: profileResponse.data.is_phone_verified || false,
              };
              
              setUser(userFromSupabase);
              localStorage.setItem('admin_user', JSON.stringify(userFromSupabase));
              setIsLoading(false);
              return true;
            }
          } catch (supabaseError) {
            console.error('Failed to get profile from Supabase:', supabaseError);
          }
          
          // If both fail, still allow login but show warning
          console.warn('Could not fetch user profile, but login succeeded');
          setIsLoading(false);
          return true; // Still return true since Supabase login succeeded
        }
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
