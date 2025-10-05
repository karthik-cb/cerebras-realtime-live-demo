import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ChevronDown, ChevronRight, Clock, Zap, Database, Mic, Brain, Volume2 } from 'lucide-react';

interface InteractionMetrics {
  metrics_id: string;
  message_id: string;
  service_type: string;
  service_name: string;
  interaction_id?: string;
  ttfb?: string;
  processing_time?: string;
  total_latency?: string;
  prompt_tokens?: number;
  completion_tokens?: number;
  characters_processed?: number;
  service_metadata?: Record<string, any>;
  created_at: string;
}

interface MetricsDisplayProps {
  metrics: InteractionMetrics[];
}

const getServiceIcon = (serviceType: string) => {
  switch (serviceType) {
    case 'stt':
      return <Mic className="h-4 w-4" />;
    case 'llm':
      return <Brain className="h-4 w-4" />;
    case 'tts':
      return <Volume2 className="h-4 w-4" />;
    case 'mcp':
      return <Database className="h-4 w-4" />;
    default:
      return <Zap className="h-4 w-4" />;
  }
};

const getServiceColor = (serviceType: string) => {
  switch (serviceType) {
    case 'stt':
      return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
    case 'llm':
      return 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200';
    case 'tts':
      return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
    case 'mcp':
      return 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200';
    default:
      return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
  }
};

const formatLatency = (latency?: string) => {
  if (!latency) return 'N/A';
  const num = parseFloat(latency);
  if (num < 0.001) return `${(num * 1000).toFixed(2)}ms`;
  return `${num.toFixed(3)}s`;
};

const formatTokens = (tokens?: number) => {
  if (!tokens) return 'N/A';
  return tokens.toLocaleString();
};

export default function MetricsDisplay({ metrics }: MetricsDisplayProps) {
  const [isOpen, setIsOpen] = useState(false);

  if (!metrics || metrics.length === 0) {
    return null;
  }

  // Group metrics by service type
  const groupedMetrics = metrics.reduce((acc, metric) => {
    if (!acc[metric.service_type]) {
      acc[metric.service_type] = [];
    }
    acc[metric.service_type].push(metric);
    return acc;
  }, {} as Record<string, InteractionMetrics[]>);

  const totalLatency = metrics.reduce((sum, metric) => {
    const latency = parseFloat(metric.total_latency || '0');
    return sum + latency;
  }, 0);

  const totalTokens = metrics.reduce((sum, metric) => {
    return sum + (metric.prompt_tokens || 0) + (metric.completion_tokens || 0);
  }, 0);

  return (
    <div className="mt-2">
      <Button
        variant="ghost"
        size="sm"
        className="h-8 px-2 text-xs text-muted-foreground hover:text-foreground"
        onClick={() => setIsOpen(!isOpen)}
      >
        {isOpen ? (
          <ChevronDown className="h-3 w-3 mr-1" />
        ) : (
          <ChevronRight className="h-3 w-3 mr-1" />
        )}
        <Clock className="h-3 w-3 mr-1" />
        Performance Metrics
        <Badge variant="secondary" className="ml-2 text-xs">
          {metrics.length}
        </Badge>
      </Button>
      
      {isOpen && (
        <div className="space-y-2 mt-2">
          {/* Summary */}
          <Card className="bg-muted/50">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Summary</CardTitle>
            </CardHeader>
            <CardContent className="pt-0">
              <div className="grid grid-cols-2 gap-4 text-xs">
                <div className="flex items-center gap-2">
                  <Clock className="h-3 w-3" />
                  <span>Total Latency: {formatLatency(totalLatency.toString())}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Zap className="h-3 w-3" />
                  <span>Total Tokens: {formatTokens(totalTokens)}</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Service Metrics */}
          {Object.entries(groupedMetrics).map(([serviceType, serviceMetrics]) => (
            <Card key={serviceType} className="bg-muted/30">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-2">
                  {getServiceIcon(serviceType)}
                  <span className="capitalize">{serviceType.toUpperCase()}</span>
                  <Badge className={getServiceColor(serviceType)}>
                    {serviceMetrics.length}
                  </Badge>
                </CardTitle>
              </CardHeader>
              <CardContent className="pt-0 space-y-2">
                {serviceMetrics.map((metric) => (
                  <div key={metric.metrics_id} className="text-xs space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="font-medium">{metric.service_name}</span>
                      <span className="text-muted-foreground">
                        {new Date(metric.created_at).toLocaleTimeString()}
                      </span>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      {metric.ttfb && (
                        <div className="flex items-center gap-1">
                          <Clock className="h-3 w-3" />
                          <span>TTFB: {formatLatency(metric.ttfb)}</span>
                        </div>
                      )}
                      {metric.processing_time && (
                        <div className="flex items-center gap-1">
                          <Zap className="h-3 w-3" />
                          <span>Process: {formatLatency(metric.processing_time)}</span>
                        </div>
                      )}
                      {metric.total_latency && (
                        <div className="flex items-center gap-1">
                          <Clock className="h-3 w-3" />
                          <span>Total: {formatLatency(metric.total_latency)}</span>
                        </div>
                      )}
                      {(metric.prompt_tokens || metric.completion_tokens) && (
                        <div className="flex items-center gap-1">
                          <Database className="h-3 w-3" />
                          <span>
                            Tokens: {formatTokens(metric.prompt_tokens)}/{formatTokens(metric.completion_tokens)}
                          </span>
                        </div>
                      )}
                      {metric.characters_processed && (
                        <div className="flex items-center gap-1">
                          <Volume2 className="h-3 w-3" />
                          <span>Chars: {formatTokens(metric.characters_processed)}</span>
                        </div>
                      )}
                    </div>

                    {metric.service_metadata && Object.keys(metric.service_metadata).length > 0 && (
                      <details className="text-xs">
                        <summary className="cursor-pointer text-muted-foreground hover:text-foreground">
                          Additional Info
                        </summary>
                        <div className="mt-1 p-2 bg-muted rounded text-xs">
                          {Object.entries(metric.service_metadata).map(([key, value]) => (
                            <div key={key} className="flex justify-between py-1">
                              <span className="text-muted-foreground capitalize">
                                {key.replace(/_/g, ' ')}:
                              </span>
                              <span className="font-medium">
                                {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                              </span>
                            </div>
                          ))}
                        </div>
                      </details>
                    )}
                  </div>
                ))}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
