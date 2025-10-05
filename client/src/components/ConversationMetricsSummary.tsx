import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ChevronDown, ChevronRight, Clock, Zap, Mic, Brain, Volume2, BarChart3, Bug, Eye, EyeOff, Table, Grid3X3 } from 'lucide-react';
import MetricsTable from './MetricsTable';

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


export default function ConversationMetricsSummary({ metrics }: ConversationMetricsSummaryProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [showDebugMode, setShowDebugMode] = useState(false);
  const [viewMode, setViewMode] = useState<'cards' | 'table'>('table');

  if (!metrics) {
    return null;
  }
  
  if (metrics.total_latency === 0) {
    return null;
  }

  const { total_messages, total_latency, total_tokens, service_breakdown } = metrics;

  return (
    <div className="mt-4 mb-4">
      <div className="flex items-center gap-2">
        <Button
          variant="outline"
          size="sm"
          className="h-12 px-4 text-sm font-medium bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200 hover:from-blue-100 hover:to-purple-100 flex-1 text-orange-600 hover:text-orange-700"
          onClick={() => setIsOpen(!isOpen)}
        >
          {isOpen ? (
            <ChevronDown className="h-4 w-4 mr-2" />
          ) : (
            <ChevronRight className="h-4 w-4 mr-2" />
          )}
          <BarChart3 className="h-4 w-4 mr-2" />
          Performance Analytics
          <Badge variant="secondary" className="ml-2">
            {total_messages} messages
          </Badge>
        </Button>
        
        <div className="flex gap-1">
          <Button
            variant="ghost"
            size="sm"
            className="h-12 px-3 text-xs text-muted-foreground hover:text-foreground"
            onClick={() => setViewMode(viewMode === 'table' ? 'cards' : 'table')}
            title={viewMode === 'table' ? "Switch to card view" : "Switch to table view"}
          >
            {viewMode === 'table' ? <Grid3X3 className="h-4 w-4" /> : <Table className="h-4 w-4" />}
          </Button>
          <Button
            variant="ghost"
            size="sm"
            className="h-12 px-3 text-xs text-muted-foreground hover:text-foreground"
            onClick={() => setShowDebugMode(!showDebugMode)}
            title={showDebugMode ? "Hide debug info" : "Show debug info"}
          >
            {showDebugMode ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
          </Button>
        </div>
      </div>
      
      {isOpen && (
        <div className="mt-4 space-y-4">
          {viewMode === 'table' ? (
            <MetricsTable metrics={metrics} />
          ) : (
            <>
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
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {Object.entries(service_breakdown).map(([serviceType, data]) => {
              if (data.count === 0) return null;
              
              const serviceNames = {
                'stt': 'Speech-to-Text',
                'llm': 'Language Model', 
                'tts': 'Text-to-Speech'
              };
              
              return (
                <Card key={serviceType} className="bg-white border-2 hover:shadow-lg transition-all duration-200">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        {getServiceIcon(serviceType)}
                        <span className="font-semibold">{serviceNames[serviceType as keyof typeof serviceNames]}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge className={getServiceColor(serviceType)}>
                          {data.count} call{data.count !== 1 ? 's' : ''}
                        </Badge>
                      </div>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="pt-0">
                    <div className="space-y-3 text-sm">
                      <div className="flex justify-between items-center">
                        <span className="text-muted-foreground">Average Response:</span>
                        <span className="font-semibold text-lg">{formatLatency(data.avg_latency)}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-muted-foreground">Total Processing:</span>
                        <span className="font-medium">{formatLatency(data.total_latency)}</span>
                      </div>
                      {data.total_tokens && (
                        <div className="flex justify-between items-center">
                          <span className="text-muted-foreground">Tokens Processed:</span>
                          <span className="font-medium">{formatTokens(data.total_tokens)}</span>
                        </div>
                      )}
                      {data.total_characters && (
                        <div className="flex justify-between items-center">
                          <span className="text-muted-foreground">Characters Generated:</span>
                          <span className="font-medium">{formatTokens(data.total_characters)}</span>
                        </div>
                      )}
                      {/* Performance bar */}
                      <div className="w-full bg-gray-100 rounded-full h-2 mt-3">
                        <div 
                          className={`h-2 rounded-full transition-all duration-500 ${
                            serviceType === 'stt' ? 'bg-blue-400' :
                            serviceType === 'llm' ? 'bg-purple-400' : 'bg-green-400'
                          }`}
                          style={{ width: `${Math.min((data.avg_latency / 2) * 100, 100)}%` }}
                        ></div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>

          {/* Performance Insights */}
          <Card className="bg-gradient-to-r from-gray-50 to-blue-50 border-gray-200">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm flex items-center gap-2">
                <Clock className="h-4 w-4" />
                Performance Insights
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-0">
              <div className="text-sm space-y-2">
                {total_latency < 1 && (
                  <div className="flex items-center gap-2 text-green-600">
                    <span className="text-lg">🚀</span>
                    <span>Excellent performance - {formatLatency(total_latency)} total response time</span>
                  </div>
                )}
                {total_latency >= 1 && total_latency < 3 && (
                  <div className="flex items-center gap-2 text-yellow-600">
                    <span className="text-lg">⚡</span>
                    <span>Good performance - {formatLatency(total_latency)} total response time</span>
                  </div>
                )}
                {total_latency >= 3 && total_latency < 5 && (
                  <div className="flex items-center gap-2 text-orange-600">
                    <span className="text-lg">⚠️</span>
                    <span>Moderate latency - {formatLatency(total_latency)} total response time</span>
                  </div>
                )}
                {total_latency >= 5 && (
                  <div className="flex items-center gap-2 text-red-600">
                    <span className="text-lg">🐌</span>
                    <span>High latency detected - {formatLatency(total_latency)} total response time</span>
                  </div>
                )}
                {total_tokens > 1000 && (
                  <div className="flex items-center gap-2 text-blue-600">
                    <span className="text-lg">📊</span>
                    <span>High token usage - {formatTokens(total_tokens)} tokens processed</span>
                  </div>
                )}
                <div className="flex items-center gap-2 text-gray-600">
                  <span className="text-lg">💡</span>
                  <span>Average response time per message: {formatLatency(total_latency / total_messages)}</span>
                </div>
              </div>
            </CardContent>
          </Card>
            </>
          )}

          {/* Debug Mode - Raw Data */}
          {showDebugMode && (
            <Card className="bg-gray-50 border-gray-200">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm flex items-center gap-2">
                  <Bug className="h-4 w-4" />
                  Debug Information
                </CardTitle>
              </CardHeader>
              <CardContent className="pt-0">
                <div className="text-xs">
                  <div className="mb-2 text-muted-foreground">Raw metrics data:</div>
                  <pre className="bg-gray-100 p-3 rounded text-xs overflow-x-auto border">
                    {JSON.stringify(metrics, null, 2)}
                  </pre>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  );
}
