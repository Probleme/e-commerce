import React, { useState } from 'react';
import { QRCodeSVG } from 'qrcode.react';
import { toast } from 'react-toastify';
import axios from '../../lib/axios';

export const TwoFactorSetup = () => {
  const [setupData, setSetupData] = useState(null);
  const [verificationCode, setVerificationCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [showBackupCodes, setShowBackupCodes] = useState(false);

  const initializeSetup = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/2fa/setup/');
      setSetupData(response.data);
    } catch (error) {
      toast.error('Failed to initialize 2FA setup');
    } finally {
      setLoading(false);
    }
  };

  const verifyAndEnable = async (e) => {
    e.preventDefault();
    if (!verificationCode) {
      toast.error('Please enter verification code');
      return;
    }

    try {
      setLoading(true);
      const response = await axios.post('/api/2fa/setup/', {
        code: verificationCode
      });
      setShowBackupCodes(true);
      toast.success('2FA enabled successfully');
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to verify code');
    } finally {
      setLoading(false);
    }
  };

  if (showBackupCodes && setupData?.backup_codes) {
    return (
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-medium mb-4">Save Your Backup Codes</h3>
        <p className="text-sm text-gray-600 mb-4">
          Store these backup codes in a safe place. Each code can only be used once.
        </p>
        <div className="grid grid-cols-2 gap-2 mb-4">
          {setupData.backup_codes.map((code, index) => (
            <div key={index} className="font-mono bg-gray-100 p-2 rounded">
              {code}
            </div>
          ))}
        </div>
        <button
          onClick={() => window.location.reload()}
          className="w-full bg-indigo-600 text-white py-2 rounded hover:bg-indigo-700"
        >
          Done
        </button>
      </div>
    );
  }

  if (!setupData) {
    return (
      <button
        onClick={initializeSetup}
        disabled={loading}
        className="bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700"
      >
        {loading ? 'Setting up...' : 'Setup Two-Factor Authentication'}
      </button>
    );
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h3 className="text-lg font-medium mb-4">Setup Two-Factor Authentication</h3>
      <p className="text-sm text-gray-600 mb-4">
        Scan this QR code with your authenticator app (like Google Authenticator)
      </p>
      
      <div className="mb-6">
        <QRCodeSVG
          value={setupData.qr_code}
          size={256}
          level="M"
          className="mx-auto"
        />
      </div>

      <form onSubmit={verifyAndEnable}>
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700">
            Enter Verification Code
          </label>
          <input
            type="text"
            value={verificationCode}
            onChange={(e) => setVerificationCode(e.target.value)}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            placeholder="Enter 6-digit code"
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-indigo-600 text-white py-2 rounded hover:bg-indigo-700"
        >
          {loading ? 'Verifying...' : 'Verify and Enable'}
        </button>
      </form>
    </div>
  );
};