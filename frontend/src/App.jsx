import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import { AuthProvider } from './contexts/AuthContext';
import { AuthLayout } from './components/AuthLayout';
import Navbar from './components/Navbar';
import Login from './pages/Login';
import Register from './pages/Register';
import Home from './pages/Home';
import { GitHubCallback } from './components/OAuth/GithubCallback';
import { GoogleCallback } from './components/OAuth/GoogleCallback';
import { TwoFactorSetup } from './components/TwoFactorAuth/TwoFactorSetup';

import 'react-toastify/dist/ReactToastify.css';

const App = () => {
  return (
    <Router>
      <AuthProvider>
        <div className="min-h-screen bg-gray-100">
          <Navbar />
          <main>
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/oauth/github/callback" element={<GitHubCallback />} />
              <Route path="/oauth/google/callback" element={<GoogleCallback />} />
              <Route
                path="/2fa/setup"
                element={
                  // <AuthLayout>
                    <TwoFactorSetup />
                  // </AuthLayout>
                }
              />
              <Route
                path="/"
                element={
                  <AuthLayout>
                    <Home />
                  </AuthLayout>
                }
              />
            </Routes>
          </main>
          <ToastContainer 
            position="top-right" 
            autoClose={3000}
            hideProgressBar={false}
            newestOnTop={true}
            closeOnClick
            rtl={false}
            pauseOnFocusLoss
            draggable
            pauseOnHover
            theme="light"
            limit={3}
            toastStyle={{
              fontSize: '14px',
              fontWeight: '500'
            }}
          />
        </div>
      </AuthProvider>
    </Router>
  );
};

export default App;