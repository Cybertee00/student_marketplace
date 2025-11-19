import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Eye, EyeOff, Lock, User } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { toast } from 'react-hot-toast';
import LoadingSpinner from '@/components/LoadingSpinner';

const loginSchema = z.object({
  identifier: z.string().min(1, 'Username, email, or phone is required'),
  password: z.string().min(1, 'Password is required'),
});

type LoginFormData = z.infer<typeof loginSchema>;

const LoginPage: React.FC = () => {
  const [showPassword, setShowPassword] = useState(false);
  const { login, isLoading, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  // Redirect if already authenticated
  React.useEffect(() => {
    // Only redirect if we're sure user is authenticated (not loading)
    if (!isLoading && isAuthenticated) {
      console.log('Redirecting to dashboard...');
      navigate('/dashboard', { replace: true });
    }
  }, [isAuthenticated, navigate, isLoading]);

  // Failsafe to avoid infinite loading states
  React.useEffect(() => {
    if (!isLoading) return;

    const timeout = setTimeout(() => {
      console.warn('Login page loading timeout - this might indicate an issue');
    }, 5000);

    return () => clearTimeout(timeout);
  }, [isLoading]);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  // Show loading spinner while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
        <p className="mt-4 text-sm text-secondary-500">Checking authentication...</p>
      </div>
    );
  }

  // Don't show login form if already authenticated
  if (isAuthenticated) {
    return null;
  }

  const onSubmit = async (data: LoginFormData) => {
    console.log('LoginPage onSubmit - starting login with:', data);
    try {
      const success = await login(data);
      console.log('LoginPage onSubmit - login result:', success);
      if (success) {
        toast.success('Login successful!');
        // Force navigation to dashboard using window.location
        setTimeout(() => {
          window.location.href = '/dashboard';
        }, 100);
      } else {
        toast.error('Invalid credentials');
      }
    } catch (error) {
      console.error('LoginPage onSubmit - error:', error);
      toast.error('Login failed. Please try again.');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-secondary-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <div className="mx-auto h-12 w-12 bg-primary-600 rounded-lg flex items-center justify-center">
            <Lock className="h-6 w-6 text-white" />
          </div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-secondary-900">
            Admin Login
          </h2>
          <p className="mt-2 text-center text-sm text-secondary-600">
            Sign in to access the Student Marketplace Admin Panel
          </p>
        </div>
        
        <form className="mt-8 space-y-6" onSubmit={handleSubmit(onSubmit)}>
          <div className="space-y-4">
            <div>
              <label htmlFor="identifier" className="block text-sm font-medium text-secondary-700">
                Username, Email, or Phone
              </label>
              <div className="mt-1 relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <User className="h-5 w-5 text-secondary-400" />
                </div>
                <input
                  {...register('identifier')}
                  type="text"
                  className="input pl-10"
                  placeholder="Enter your identifier"
                />
              </div>
              {errors.identifier && (
                <p className="mt-1 text-sm text-danger-600">{errors.identifier.message}</p>
              )}
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-secondary-700">
                Password
              </label>
              <div className="mt-1 relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-5 w-5 text-secondary-400" />
                </div>
                <input
                  {...register('password')}
                  type={showPassword ? 'text' : 'password'}
                  className="input pl-10 pr-10"
                  placeholder="Enter your password"
                />
                <button
                  type="button"
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? (
                    <EyeOff className="h-5 w-5 text-secondary-400" />
                  ) : (
                    <Eye className="h-5 w-5 text-secondary-400" />
                  )}
                </button>
              </div>
              {errors.password && (
                <p className="mt-1 text-sm text-danger-600">{errors.password.message}</p>
              )}
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={isLoading}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <LoadingSpinner size="sm" className="text-white" />
              ) : (
                'Sign in'
              )}
            </button>
          </div>

          <div className="text-center">
            <p className="text-sm text-secondary-600">
              Demo Credentials:
            </p>
            <p className="text-xs text-secondary-500 mt-1">
              Email: admin@university.edu<br />
              Password: admin123
            </p>
          </div>
        </form>
      </div>
    </div>
  );
};

export default LoginPage;
