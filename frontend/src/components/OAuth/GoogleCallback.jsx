import React, { useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { toast } from 'react-toastify';

export const GoogleCallback = () => {
  const navigate = useNavigate();
  const { handleOAuthCallback } = useAuth();
  const isProcessing = useRef(false);

  useEffect(() => {
    const handleCallback = async () => {
      if (isProcessing.current) {
        return;
      }

      const params = new URLSearchParams(window.location.search);
      const code = params.get('code');
      
      if (!code) {
        toast.error('Authentication failed: No code received');
        navigate('/login');
        return;
      }

      try {
        isProcessing.current = true;
        await handleOAuthCallback('google', code);
        toast.success('Successfully signed in with Google');
        navigate('/');
      } catch (error) {
        console.error('Google auth error:', error);
        toast.error(error.response?.data?.error || 'Authentication failed');
        navigate('/login');
      } finally {
        isProcessing.current = false;
      }
    };

    handleCallback();
  }, []);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
        <h2 className="text-xl font-semibold mb-2">Authenticating with Google...</h2>
        <p className="text-gray-600">Please wait while we complete your sign in.</p>
      </div>
    </div>
  );
};