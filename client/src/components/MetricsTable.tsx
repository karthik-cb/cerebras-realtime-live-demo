import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Mic, Brain, Volume2, Clock, Zap, Database } from 'lucide-react';

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
  };
}

interface MetricsTableProps {
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
    default:
      return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
  }
};

const formatLatency = (latency: number) => {
  if (latency < 0.001) return `${(latency * 1000).toFixed(1)}ms`;
  if (latency < 1) return `${(latency * 1000).toFixed(0)}ms`;
  return `${latency.toFixed(2)}s`;
};

const formatTokens = (tokens: number) => {
  if (tokens >= 1000) {
    return `${(tokens / 1000).toFixed(1)}k`;
  }
  return tokens.toLocaleString();
};


export default function MetricsTable({ metrics }: MetricsTableProps) {
  const { total_messages, total_latency, total_tokens, service_breakdown } = metrics;

  const serviceNames = {
    'stt': 'Speech-to-Text',
    'llm': 'Language Model', 
    'tts': 'Text-to-Speech'
  };

  return (
    <div className="space-y-4">
      {/* Overall Summary Table */}
      <Card className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-950/20 dark:to-purple-950/20">
        <CardHeader className="pb-3">
          <CardTitle className="text-lg flex items-center gap-2">
            <Database className="h-5 w-5" />
            Conversation Overview
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-2 font-medium text-muted-foreground">Metric</th>
                  <th className="text-right py-2 font-medium text-muted-foreground">Value</th>
                  <th className="text-right py-2 font-medium text-muted-foreground">Per Message</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                <tr>
                  <td className="py-2 font-medium">Total Messages</td>
                  <td className="py-2 text-right font-bold text-blue-600">{total_messages}</td>
                  <td className="py-2 text-right text-muted-foreground">—</td>
                </tr>
                <tr>
                  <td className="py-2 font-medium">Total Response Time</td>
                  <td className="py-2 text-right font-bold text-green-600">{formatLatency(total_latency)}</td>
                  <td className="py-2 text-right font-medium">{formatLatency(total_latency / total_messages)}</td>
                </tr>
                <tr>
                  <td className="py-2 font-medium">Total Tokens</td>
                  <td className="py-2 text-right font-bold text-purple-600">{formatTokens(total_tokens)}</td>
                  <td className="py-2 text-right font-medium">{formatTokens(Math.round(total_tokens / total_messages))}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Service Breakdown Table */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-lg flex items-center gap-2">
            <Clock className="h-5 w-5" />
            Service Performance Breakdown
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-2 font-medium text-muted-foreground">Service</th>
                  <th className="text-right py-2 font-medium text-muted-foreground">Calls</th>
                  <th className="text-right py-2 font-medium text-muted-foreground">Avg Response</th>
                  <th className="text-right py-2 font-medium text-muted-foreground">Total Time</th>
                  <th className="text-right py-2 font-medium text-muted-foreground">Usage</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {Object.entries(service_breakdown).map(([serviceType, data]) => {
                  if (data.count === 0) return null;
                  
                  return (
                    <tr key={serviceType} className="hover:bg-muted/50">
                      <td className="py-3">
                        <div className="flex items-center gap-2">
                          {getServiceIcon(serviceType)}
                          <span className="font-medium">{serviceNames[serviceType as keyof typeof serviceNames]}</span>
                        </div>
                      </td>
                      <td className="py-3 text-right">
                        <Badge className={getServiceColor(serviceType)}>
                          {data.count}
                        </Badge>
                      </td>
                      <td className="py-3 text-right font-semibold">
                        {formatLatency(data.avg_latency)}
                      </td>
                      <td className="py-3 text-right font-medium">
                        {formatLatency(data.total_latency)}
                      </td>
                      <td className="py-3 text-right text-muted-foreground">
                        {data.total_tokens && (
                          <div className="text-xs">
                            <div className="font-medium">{formatTokens(data.total_tokens)} tokens</div>
                          </div>
                        )}
                        {data.total_characters && (
                          <div className="text-xs">
                            <div className="font-medium">{formatTokens(data.total_characters)} chars</div>
                          </div>
                        )}
                        {!data.total_tokens && !data.total_characters && (
                          <div className="text-xs text-muted-foreground">—</div>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
