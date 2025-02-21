import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from '../lib/axios';
import { toast } from 'react-toastify';
import { useNavigate, useLocation } from 'react-router-dom';

const AuthContext = createContext({});

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const location = useLocation();

  // Check if current path is login or register
  const isAuthPage = (pathname) => {
    return pathname === '/login' || pathname === '/register';
  };

  const checkAuth = async () => {
    try {
      const response = await axios.get('/api/user/');
      
      if (response.status === 200 && response.data) {
        setUser(true);
        console.log('User:', response.data);
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
      setUser(response.data.user);
      toast.success('Login successful');
      await checkAuth(); // This will handle the redirect
      return response.data;
    } catch (error) {
      toast.error(error.response?.data?.error || 'Login failed');
    }
  };

  const logout = async () => {
    try {
      await axios.post('/api/logout/');
      setUser(null);
      toast.success('Logout successful');
      navigate('/login');
    } catch (error) {
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
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);