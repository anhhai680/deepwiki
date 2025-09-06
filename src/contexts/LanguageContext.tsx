/* eslint-disable @typescript-eslint/no-explicit-any */
'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

type Messages = Record<string, any>;
type LanguageContextType = {
  language: string;
  messages: Messages;
};

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export function LanguageProvider({ children }: { children: ReactNode }) {
  // Always use English - no language switching needed
  const [messages, setMessages] = useState<Messages>({});
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const loadEnglishMessages = async () => {
      try {
        // Always load English messages
        const enMessages = (await import('../messages/en.json')).default;
        setMessages(enMessages);

        // Update HTML lang attribute to English
        if (typeof document !== 'undefined') {
          document.documentElement.lang = 'en';
        }
      } catch (error) {
        console.error('Failed to load English messages:', error);
        // Set empty messages as fallback
        setMessages({});
      } finally {
        setIsLoading(false);
      }
    };
    
    loadEnglishMessages();
  }, []);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-100 dark:bg-gray-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-500 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <LanguageContext.Provider value={{ language: 'en', messages }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (context === undefined) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
}
