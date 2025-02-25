import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from '../lib/axios';
import { toast } from 'react-toastify';
import { useNavigate, useLocation } from 'react-router-dom';

const AuthContext = createContext({});

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const [show2FA, setShow2FA] = useState(false);
  const [tempUserId, setTempUserId] = useState(null);

  const GITHUB_CLIENT_ID = 'Ov23liHht6qmgiI2f2lv';
  const GOOGLE_CLIENT_ID = '76356682659-fhjbt0o9b6cf085mhd4b4vhpdssglmvu.apps.googleusercontent.com';
  
  const GITHUB_REDIRECT_URI = `https://127.0.0.1:8002/oauth/github/callback`;
  const GOOGLE_REDIRECT_URI = `https://localhost:8002/oauth/google/callback`;

  // Check if current path is login, register, or oauth callback
  const isAuthPage = (pathname) => {
    return pathname === '/login' || 
           pathname === '/register';
  };

  const checkAuth = async () => {
    try {
      const response = await axios.get('/api/user/');
      
      if (response.status === 200 && response.data) {
        setUser(response.data);
        // If user is authenticated and on login/register page, redirect to home
        if (isAuthPage(window.location.pathname)) {
          navigate('/');
        }
      } else {
        setUser(null);
        // Only redirect to login if not already on an auth page
        if (!isAuthPage(window.location.pathname)) {
          navigate('/login');
        }
      }
    } catch (error) {
      setUser(null);
      // Only redirect to login if not already on an auth page
      if (!isAuthPage(window.location.pathname)) {
        navigate('/login');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkAuth();
  }, []);

  const login = async (email, password) => {
    try {
      const response = await axios.post('/api/login/', { email, password });

      // Check if 2FA is required
      if (response.data.requires_2fa) {
        setTempUserId(response.data.user_id);
        setShow2FA(true);
        return;
      }

      setUser(response.data.user);
      
      // Set authorization header
      if (response.data.access_token) {
        axios.defaults.headers.common['Authorization'] = `Bearer ${response.data.access_token}`;
      }

      await checkAuth();

      // toast.success('Login successful');
      // navigate('/');
      return response.data;
    } catch (error) {
      toast.error(error.response?.data?.error || 'Login failed');
      throw error;
    }
  };

  const verify2FA = async (code) => {
    try {
      const response = await axios.post('/api/2fa/verify/', {
        user_id: tempUserId,
        code
      });

      setUser(response.data.user);
      setShow2FA(false);
      setTempUserId(null);

      await checkAuth();

      toast.success('Login successful');
      navigate('/');
    } catch (error) {
      toast.error(error.response?.data?.error || 'Invalid verification code');
      throw error;
    }
  };

  const loginWithGitHub = () => {
    const githubUrl = `https://github.com/login/oauth/authorize?client_id=${GITHUB_CLIENT_ID}&redirect_uri=${GITHUB_REDIRECT_URI}&scope=user:email`;
    window.location.href = githubUrl;
  };

  const loginWithGoogle = () => {
    const googleUrl = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${GOOGLE_CLIENT_ID}&redirect_uri=${GOOGLE_REDIRECT_URI}&response_type=code&scope=email profile`;
    window.location.href = googleUrl;
  };

  const handleOAuthCallback = async (provider, code) => {
    try {
      const response = await axios.post(`/api/oauth/${provider}/`, { code });
      await checkAuth();
      setUser(response.data.user);
      return response.data;
    } catch (error) {
      toast.error(error.response?.data?.error || `${provider} login failed`);
      navigate('/login');
    }
  };

  const logout = async () => {
    try {
      await axios.post('/api/logout/');
      
      // Clear auth header
      delete axios.defaults.headers.common['Authorization'];

      await checkAuth();
      
      // Clear user state
      setUser(null);
      
      toast.success('Logout successful');
      navigate('/login');
    } catch (error) {
      console.error('Logout error:', error);
      toast.error('Logout failed');
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        login,
        logout,
        loading,
        checkAuth,
        loginWithGitHub,
        loginWithGoogle,
        handleOAuthCallback,
        isAuthenticated: !!user,
        show2FA,
        setShow2FA,
        verify2FA,
        tempUserId,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};