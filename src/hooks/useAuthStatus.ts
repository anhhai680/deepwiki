import { useState, useEffect, useCallback } from 'react';

interface AuthState {
  authRequired: boolean;
  authCode: string;
  isAuthLoading: boolean;
}

export const useAuthStatus = () => {
  const [authState, setAuthState] = useState<AuthState>({
    authRequired: false,
    authCode: '',
    isAuthLoading: true,
  });

  // Fetch authentication status from API
  const fetchAuthStatus = useCallback(async () => {
    try {
      setAuthState(prev => ({ ...prev, isAuthLoading: true }));
      const response = await fetch('/api/auth/status');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setAuthState(prev => ({
        ...prev,
        authRequired: data.auth_required,
        isAuthLoading: false,
      }));
    } catch (error) {
      console.error('Failed to fetch auth status:', error);
      setAuthState(prev => ({ 
        ...prev, 
        authRequired: false, 
        isAuthLoading: false,
      }));
    }
  }, []);

  // Validate authentication code
  const validateAuthCode = useCallback(async (code: string): Promise<boolean> => {
    try {
      const response = await fetch('/api/auth/validate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ auth_code: code }),
      });

      if (!response.ok) {
        return false;
      }

      const data = await response.json();
      return data.valid === true;
    } catch (error) {
      console.error('Failed to validate auth code:', error);
      return false;
    }
  }, []);

  // Set auth code
  const setAuthCode = useCallback((code: string) => {
    setAuthState(prev => ({ ...prev, authCode: code }));
  }, []);

  // Initialize auth status on mount
  useEffect(() => {
    fetchAuthStatus();
  }, [fetchAuthStatus]);

  return {
    authState,
    setAuthCode,
    validateAuthCode,
    refetchAuthStatus: fetchAuthStatus,
  };
};
