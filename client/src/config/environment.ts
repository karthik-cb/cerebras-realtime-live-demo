/**
 * Environment configuration for the voice agent demo
 * This file centralizes environment variable access and provides fallbacks
 */

interface EnvironmentConfig {
  serverUrl: string;
  deepgramApiKey: string;
  cerebrasApiKey: string;
  dailyApiKey: string;
  paypalClientId: string;
  paypalClientSecret: string;
  paypalEnvironment: 'SANDBOX' | 'PRODUCTION';
  isDevelopment: boolean;
  isProduction: boolean;
}

// Get environment variables with fallbacks
const getEnvVar = (key: string, fallback: string = ''): string => {
  return import.meta.env[key] || fallback;
};

// Validate required environment variables
const validateRequiredEnvVars = (): void => {
  const required = ['VITE_SERVER_URL'];
  const missing = required.filter(key => !import.meta.env[key]);
  
  if (missing.length > 0) {
    console.warn(`Missing required environment variables: ${missing.join(', ')}`);
    console.warn('Please check your .env.local file or Vercel environment variables');
  }
};

// Configuration object
export const config: EnvironmentConfig = {
  // Server configuration
  serverUrl: getEnvVar('VITE_SERVER_URL', 'http://localhost:7860/api'),
  
  // API Keys (these should be set in Vercel environment variables)
  deepgramApiKey: getEnvVar('DEEPGRAM_API_KEY'),
  cerebrasApiKey: getEnvVar('CEREBRAS_API_KEY'),
  dailyApiKey: getEnvVar('DAILY_API_KEY'),
  
  // PayPal configuration
  paypalClientId: getEnvVar('PAYPAL_CLIENT_ID'),
  paypalClientSecret: getEnvVar('PAYPAL_CLIENT_SECRET'),
  paypalEnvironment: (getEnvVar('PAYPAL_ENVIRONMENT', 'SANDBOX') as 'SANDBOX' | 'PRODUCTION'),
  
  // Environment detection
  isDevelopment: import.meta.env.DEV,
  isProduction: import.meta.env.PROD,
};

// Validate configuration on import
if (config.isDevelopment) {
  validateRequiredEnvVars();
}

// Helper functions
export const isApiKeyConfigured = (key: keyof Pick<EnvironmentConfig, 'deepgramApiKey' | 'cerebrasApiKey' | 'dailyApiKey'>): boolean => {
  return !!config[key];
};

export const getConfiguredServices = (): string[] => {
  const services: string[] = [];
  
  if (isApiKeyConfigured('deepgramApiKey')) services.push('Deepgram (STT/TTS)');
  if (isApiKeyConfigured('cerebrasApiKey')) services.push('Cerebras (LLM)');
  if (isApiKeyConfigured('dailyApiKey')) services.push('Daily (WebRTC)');
  
  return services;
};

export const getMissingServices = (): string[] => {
  const allServices = ['Deepgram (STT/TTS)', 'Cerebras (LLM)', 'Daily (WebRTC)'];
  const configured = getConfiguredServices();
  return allServices.filter(service => !configured.includes(service));
};

// Export default
export default config;
