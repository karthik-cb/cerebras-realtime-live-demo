import React from 'react';
import { config, getConfiguredServices, getMissingServices } from '../config/environment';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { CheckCircle, XCircle, AlertCircle } from 'lucide-react';

interface EnvironmentStatusProps {
  className?: string;
}

export function EnvironmentStatus({ className }: EnvironmentStatusProps) {
  const configuredServices = getConfiguredServices();
  const missingServices = getMissingServices();
  const isFullyConfigured = missingServices.length === 0;

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          {isFullyConfigured ? (
            <CheckCircle className="h-5 w-5 text-green-500" />
          ) : (
            <AlertCircle className="h-5 w-5 text-yellow-500" />
          )}
          Environment Status
        </CardTitle>
        <CardDescription>
          Current configuration status for your voice agent demo
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Server Configuration */}
        <div>
          <h4 className="font-medium mb-2">Server Configuration</h4>
          <div className="flex items-center gap-2">
            <Badge variant={config.serverUrl ? "default" : "destructive"}>
              {config.serverUrl ? "Connected" : "Not Configured"}
            </Badge>
            <span className="text-sm text-muted-foreground">
              {config.serverUrl || "VITE_SERVER_URL not set"}
            </span>
          </div>
        </div>

        {/* Configured Services */}
        {configuredServices.length > 0 && (
          <div>
            <h4 className="font-medium mb-2">Configured Services</h4>
            <div className="flex flex-wrap gap-2">
              {configuredServices.map((service) => (
                <Badge key={service} variant="default" className="flex items-center gap-1">
                  <CheckCircle className="h-3 w-3" />
                  {service}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* Missing Services */}
        {missingServices.length > 0 && (
          <div>
            <h4 className="font-medium mb-2">Missing Services</h4>
            <div className="flex flex-wrap gap-2">
              {missingServices.map((service) => (
                <Badge key={service} variant="destructive" className="flex items-center gap-1">
                  <XCircle className="h-3 w-3" />
                  {service}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* PayPal Configuration */}
        {(config.paypalClientId || config.paypalClientSecret) && (
          <div>
            <h4 className="font-medium mb-2">PayPal Integration</h4>
            <div className="flex items-center gap-2">
              <Badge variant={config.paypalClientId && config.paypalClientSecret ? "default" : "destructive"}>
                {config.paypalClientId && config.paypalClientSecret ? "Configured" : "Incomplete"}
              </Badge>
              <span className="text-sm text-muted-foreground">
                Environment: {config.paypalEnvironment}
              </span>
            </div>
          </div>
        )}

        {/* Setup Instructions */}
        {!isFullyConfigured && (
          <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-md">
            <h4 className="font-medium text-yellow-800 mb-2">Setup Required</h4>
            <p className="text-sm text-yellow-700 mb-2">
              To use all features, you need to configure the missing services:
            </p>
            <ul className="text-sm text-yellow-700 list-disc list-inside space-y-1">
              {missingServices.map((service) => (
                <li key={service}>
                  {service === 'Deepgram (STT/TTS)' && 'Get your API key from Deepgram Console'}
                  {service === 'Cerebras (LLM)' && 'Get your API key from Cerebras Cloud'}
                  {service === 'Daily (WebRTC)' && 'Get your API key from Daily Dashboard (optional)'}
                </li>
              ))}
            </ul>
            <p className="text-sm text-yellow-700 mt-2">
              Add these as environment variables in your Vercel dashboard or .env.local file.
            </p>
          </div>
        )}

        {/* Environment Info */}
        <div className="pt-4 border-t">
          <h4 className="font-medium mb-2">Environment Info</h4>
          <div className="text-sm text-muted-foreground space-y-1">
            <div>Mode: {config.isDevelopment ? 'Development' : 'Production'}</div>
            <div>Server URL: {config.serverUrl}</div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
