import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ChevronDown, ChevronRight, Clock, Zap, Database, Mic, Brain, Volume2, BarChart3 } from 'lucide-react';

interface ServiceBreakdown {
  count: number;
  total_latency: number;
  avg_latency: number;
  total_tokens?: number;
  total_characters?: number;
}

interface ConversationMetricsSummary {
  total_messages: number;
  total_latency: number;
  total_tokens: number;
  service_breakdown: {
    stt: ServiceBreakdown;
    llm: ServiceBreakdown;
    tts: ServiceBreakdown;
    mcp: ServiceBreakdown;
  };
}

interface ConversationMetricsSummaryProps {
  metrics: ConversationMetricsSummary;
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

const formatLatency = (latency: number) => {
  if (latency < 0.001) return `${(latency * 1000).toFixed(2)}ms`;
  return `${latency.toFixed(3)}s`;
};

const formatTokens = (tokens: number) => {
  return tokens.toLocaleString();
};

export default function ConversationMetricsSummary({ metrics }: ConversationMetricsSummaryProps) {
  const [isOpen, setIsOpen] = useState(false);

  if (!metrics || metrics.total_latency === 0) {
    return null;
  }

  const { total_messages, total_latency, total_tokens, service_breakdown } = metrics;

  return (
    <div className="mt-4 mb-4">
      <Button
        variant="outline"
        size="sm"
        className="h-10 px-4 text-sm font-medium"
        onClick={() => setIsOpen(!isOpen)}
      >
        {isOpen ? (
          <ChevronDown className="h-4 w-4 mr-2" />
        ) : (
          <ChevronRight className="h-4 w-4 mr-2" />
        )}
        <BarChart3 className="h-4 w-4 mr-2" />
        Conversation Performance Summary
        <Badge variant="secondary" className="ml-2">
          {total_messages} messages
        </Badge>
      </Button>
      
      {isOpen && (
        <div className="mt-4 space-y-4">
          {/* Overall Summary */}
          <Card className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-950/20 dark:to-purple-950/20">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg flex items-center gap-2">
                <BarChart3 className="h-5 w-5" />
                Overall Performance
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-0">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">{total_messages}</div>
                  <div className="text-sm text-muted-foreground">Messages</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">{formatLatency(total_latency)}</div>
                  <div className="text-sm text-muted-foreground">Total Latency</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-600">{formatTokens(total_tokens)}</div>
                  <div className="text-sm text-muted-foreground">Total Tokens</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-orange-600">
                    {formatLatency(total_latency / total_messages)}
                  </div>
                  <div className="text-sm text-muted-foreground">Avg per Message</div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Service Breakdown */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {Object.entries(service_breakdown).map(([serviceType, data]) => {
              if (data.count === 0) return null;
              
              return (
                <Card key={serviceType} className="bg-muted/30">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm flex items-center gap-2">
                      {getServiceIcon(serviceType)}
                      <span className="capitalize">{serviceType.toUpperCase()}</span>
                      <Badge className={getServiceColor(serviceType)}>
                        {data.count} calls
                      </Badge>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="pt-0">
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Total Latency:</span>
                        <span className="font-medium">{formatLatency(data.total_latency)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Avg Latency:</span>
                        <span className="font-medium">{formatLatency(data.avg_latency)}</span>
                      </div>
                      {data.total_tokens && (
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Tokens:</span>
                          <span className="font-medium">{formatTokens(data.total_tokens)}</span>
                        </div>
                      )}
                      {data.total_characters && (
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Characters:</span>
                          <span className="font-medium">{formatTokens(data.total_characters)}</span>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>

          {/* Performance Insights */}
          <Card className="bg-muted/20">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm flex items-center gap-2">
                <Clock className="h-4 w-4" />
                Performance Insights
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-0">
              <div className="text-sm space-y-1">
                {total_latency < 5 && (
                  <div className="text-green-600">✅ Excellent performance - under 5 seconds total</div>
                )}
                {total_latency >= 5 && total_latency < 15 && (
                  <div className="text-yellow-600">⚠️ Good performance - {formatLatency(total_latency)} total latency</div>
                )}
                {total_latency >= 15 && (
                  <div className="text-red-600">❌ High latency detected - {formatLatency(total_latency)} total latency</div>
                )}
                {total_tokens > 1000 && (
                  <div className="text-blue-600">📊 High token usage - {formatTokens(total_tokens)} tokens processed</div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
