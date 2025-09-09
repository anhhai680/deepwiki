export const extractUrlPath = (url: string): string => {
  try {
    const urlObj = new URL(url);
    return urlObj.pathname;
  } catch {
    return url;
  }
};

export const extractUrlDomain = (url: string): string => {
  try {
    const urlObj = new URL(url);
    return urlObj.hostname;
  } catch {
    return '';
  }
};

export const createTranslationFunction = (messages: Record<string, unknown>) => {
  return (key: string, params: Record<string, string | number> = {}): string => {
    // Split the key by dots to access nested properties
    const keys = key.split('.');
    let value: unknown = messages;

    // Navigate through the nested properties
    for (const k of keys) {
      if (value && typeof value === 'object' && value !== null && k in value) {
        value = (value as Record<string, unknown>)[k];
      } else {
        // Return the key if the translation is not found
        return key;
      }
    }

    // If the value is a string, replace parameters
    if (typeof value === 'string') {
      return Object.entries(params).reduce((acc: string, [paramKey, paramValue]) => {
        return acc.replace(`{${paramKey}}`, String(paramValue));
      }, value);
    }

    // Return the key if the value is not a string
    return key;
  };
};
