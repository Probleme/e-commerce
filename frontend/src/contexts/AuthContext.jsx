import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from '../lib/axios';
import { toast } from 'react-toastify';

const AuthContext = createContext({});

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const response = await axios.get('/api/user/');
      if (response.data) {
        setUser(true);
      } else {
        setUser(null);
        if (window.location.pathname !== '/login') {
            console.log('window.location.pathname1', window.location.pathname);
          window.location.href = '/login';
        }
      }
    } catch (error) {
      setUser(null);
      if (window.location.pathname !== '/login') {
        console.log('window.location.pathname2', window.location.pathname);
        window.location.href = '/login';
      }
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    try {
      const response = await axios.post('/api/login/', { email, password });
      setUser(response.data.user);
      toast.success('Login successful!');
      return response.data;
    } catch (error) {
      toast.error(error.response?.data?.error || 'Login failed');
    }
  };

  const register = async (email, password, password2) => {
    try {
      const response = await axios.post('/api/register/', {
        email,
        password,
        password2,
      });
      toast.success('Registration successful! Please login.');
      return response.data;
    } catch (error) {
      toast.error(error.response?.data?.error || 'Registration failed');
    }
  };

  const logout = async () => {
    try {
      await axios.post('/api/logout/');
      setUser(null);
      toast.success('Logout successful');
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
        register,
        loading,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);