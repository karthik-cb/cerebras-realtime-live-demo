import BotReadyAudio from "@/components/BotReadyAudio";
import { VoiceIndicator } from "@/components/VoiceIndicator";
import { Button } from "@/components/ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";
import { RTVIEvent } from "@pipecat-ai/client-js";
import {
  useRTVIClient,
  useRTVIClientEvent,
  useRTVIClientTransportState,
} from "@pipecat-ai/client-react";
import { HistoryIcon, MicIcon, MicOffIcon, XIcon } from "lucide-react";
import { useCallback, useEffect, useState } from "react";

export const WebSocketVoiceChat: React.FC = () => {
  const [botSpeaking, setBotSpeaking] = useState(false);
  const [localAudioLevel, setLocalAudioLevel] = useState(0);
  const [muted, setMuted] = useState(false);
  const [showHistoryPopup, setShowHistoryPopup] = useState(false);
  const [conversationHistory, setConversationHistory] = useState<Array<{
    role: "user" | "assistant" | "tool";
    content: string;
    timestamp: string;
    metadata?: any;
  }>>([]);

  const rtviClient = useRTVIClient();

  const state = useRTVIClientTransportState();

  useEffect(() => {
    if (!rtviClient) return;
    rtviClient.initDevices().then(() => rtviClient.connect());
  }, [rtviClient]);

  useRTVIClientEvent(
    RTVIEvent.LocalAudioLevel,
    useCallback((level: number) => {
      setLocalAudioLevel(level);
    }, []),
  );
  useRTVIClientEvent(
    RTVIEvent.BotStartedSpeaking,
    useCallback(() => {
      setBotSpeaking(true);
    }, []),
  );
  useRTVIClientEvent(
    RTVIEvent.BotStoppedSpeaking,
    useCallback(() => {
      setBotSpeaking(false);
    }, []),
  );

  // Capture user speech
  useRTVIClientEvent(
    RTVIEvent.UserTranscript,
    useCallback((data: any) => {
      if (data.final && data.text.trim()) {
        setConversationHistory(prev => [...prev, {
          role: "user",
          content: data.text,
          timestamp: new Date().toISOString()
        }]);
      }
    }, []),
  );

  // Capture LLM text responses (the actual AI response before TTS)
  useRTVIClientEvent(
    RTVIEvent.BotLlmText,
    useCallback((data: any) => {
      if (data.text && data.text.trim()) {
        setConversationHistory(prev => {
          const lastMessage = prev[prev.length - 1];
          if (lastMessage && lastMessage.role === "assistant") {
            // Append to existing bot message
            return prev.map((msg, idx) => 
              idx === prev.length - 1 
                ? { ...msg, content: msg.content + data.text }
                : msg
            );
          } else {
            // Create new bot message
            return [...prev, {
              role: "assistant",
              content: data.text,
              timestamp: new Date().toISOString()
            }];
          }
        });
      }
    }, []),
  );

  // Capture bot TTS responses (what the user actually hears)
  useRTVIClientEvent(
    RTVIEvent.BotTtsText,
    useCallback((data: any) => {
      // This is what the user hears, but we already captured the LLM text above
      // We could use this to show what was actually spoken vs what was generated
      console.log("TTS Text (spoken):", data.text);
    }, []),
  );

  // Capture any other events that might contain tool calls or metadata
  useEffect(() => {
    if (!rtviClient) return;

    const handleAnyEvent = (eventName: string, data: any) => {
      // Log all events to see what's available
      if (eventName.includes('tool') || eventName.includes('mcp') || eventName.includes('action')) {
        console.log(`Tool/MCP Event: ${eventName}`, data);
        
        // Add tool call to conversation history
        setConversationHistory(prev => [...prev, {
          role: "tool",
          content: `Tool call: ${eventName}`,
          timestamp: new Date().toISOString(),
          metadata: data
        }]);
      }
    };

    // Listen to all events
    const eventNames = Object.keys(RTVIEvent) as Array<keyof typeof RTVIEvent>;
    eventNames.forEach(eventName => {
      // Convert PascalCase to camelCase for the listener
      const camelCaseEventName = eventName.charAt(0).toLowerCase() + eventName.slice(1);
      rtviClient.addListener(camelCaseEventName as any, (data: any) => handleAnyEvent(eventName, data));
    });

    return () => {
      eventNames.forEach(eventName => {
        const camelCaseEventName = eventName.charAt(0).toLowerCase() + eventName.slice(1);
        rtviClient.removeListener(camelCaseEventName as any, handleAnyEvent);
      });
    };
  }, [rtviClient]);
  useEffect(() => {
    if (!rtviClient) return;
    rtviClient.enableMic(!muted);
  }, [muted, rtviClient]);

  const handleDisconnect = () => {
    const conversationId = (rtviClient?.params?.requestData as any)?.conversation_id;
    console.log("🚪 Voice chat disconnect initiated:", {
      currentUrl: window.location.href,
      conversationId
    });
    rtviClient?.disconnect();
    setTimeout(() => {
      console.log("🔄 Reloading page after disconnect");
      if (conversationId) {
        // Preserve the conversation ID in the URL so it can be loaded after reload
        const searchParams = new URLSearchParams();
        searchParams.append("c", conversationId);
        history.replaceState(null, "", `/?${searchParams.toString()}`);
        console.log("✅ Preserved conversation ID in URL:", conversationId);
      }
      window.location.reload();
    }, 500);
  };

  const speakingOutline = !muted
    ? `${Math.ceil(32 * localAudioLevel)}px`
    : undefined;

  const isConnected = state === "connected" || state === "ready";
  const isError = state === "error";
  const isDisconnected =
    state === "disconnected" ||
    state === "disconnecting" ||
    state === "initialized";
  const isConnecting = !isConnected && !isError && !isDisconnected;

  return (
    <div className="flex-grow flex flex-col gap-20 sm:gap-28 items-center justify-center">
      <BotReadyAudio active={isConnecting || isConnected} />
      <VoiceIndicator
        animate
        status={
          isConnecting
            ? "connecting"
            : botSpeaking
              ? "speaking"
              : isDisconnected
                ? "disconnected"
                : "idle"
        }
      />
      <div className="flex flex-col gap-8 items-center justify-center">
        <span>
          {isDisconnected
            ? " "
            : isConnecting
              ? "Connecting…"
              : isConnected
                ? "Connected"
                : "Error"}
        </span>
        {isConnecting && (
          <div className="text-center text-sm text-muted-foreground max-w-md">
            <p>Please wait for the beep to ensure you are connected.</p>
          </div>
        )}
        <div className="flex items-center gap-8">
          {/* History Button - Show if there's current session history */}
          {conversationHistory.length > 0 && (
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    className="rounded-full p-4 h-auto"
                    onClick={() => setShowHistoryPopup(true)}
                    variant="secondary-outline"
                  >
                    <HistoryIcon size={24} />
                  </Button>
                </TooltipTrigger>
                <TooltipContent className="bg-secondary text-secondary-foreground">
                  View current session history
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          )}
          
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  className={cn(
                    "rounded-full p-4 sm:p-8 h-auto transition-all",
                    {
                      "outline outline-4": state !== "disconnected",
                      "text-destructive border-destructive outline-destructive -outline-offset-4":
                        state !== "disconnected" && muted,
                      "border-primary outline-primary/50":
                        state !== "disconnected" && !muted,
                    },
                  )}
                  style={
                    muted
                      ? {}
                      : {
                          outlineWidth: speakingOutline,
                          outlineOffset: `-${speakingOutline}`,
                        }
                  }
                  disabled={state === "disconnected"}
                  onClick={() => setMuted((m) => !m)}
                  variant="secondary-outline"
                >
                  {muted ? (
                    <MicOffIcon className="h-10 w-10 sm:h-16 sm:w-16" />
                  ) : (
                    <MicIcon className="h-10 w-10 sm:h-16 sm:w-16" />
                  )}
                </Button>
              </TooltipTrigger>
              <TooltipContent className="bg-secondary text-secondary-foreground">
                {muted ? "Unmute microphone" : "Mute microphone"}
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  className="rounded-full p-4 h-auto"
                  onClick={handleDisconnect}
                  variant="secondary-outline"
                >
                  <XIcon size={32} />
                </Button>
              </TooltipTrigger>
              <TooltipContent className="bg-secondary text-secondary-foreground">
                End voice to voice chat
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </div>
      </div>

      {/* Conversation History Popup */}
      {showHistoryPopup && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-background rounded-lg max-w-4xl max-h-[80vh] w-full flex flex-col">
            <div className="flex items-center justify-between p-6 border-b">
              <div className="flex items-center gap-2">
                <HistoryIcon className="h-5 w-5" />
                <h2 className="text-lg font-semibold">Current Session History</h2>
              </div>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setShowHistoryPopup(false)}
              >
                <XIcon className="h-4 w-4" />
              </Button>
            </div>
            
            <div className="flex-1 overflow-y-auto p-6">
              <div className="space-y-4">
                {conversationHistory.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground">
                    No conversation history yet. Start talking to see your conversation here.
                  </div>
                ) : (
                  conversationHistory.map((message, index) => {
                    const isUser = message.role === "user";
                    const isTool = message.role === "tool";
                    
                    return (
                      <div
                        key={index}
                        className={cn(
                          "p-4 rounded-lg border",
                          {
                            "bg-blue-50 border-blue-200 ml-8": isUser,
                            "bg-green-50 border-green-200 mr-8": !isUser && !isTool,
                            "bg-yellow-50 border-yellow-200 mr-8": isTool,
                          }
                        )}
                      >
                        <div className="flex items-center gap-2 mb-2">
                          <span className={cn(
                            "text-xs font-medium px-2 py-1 rounded-full",
                            {
                              "bg-blue-100 text-blue-800": isUser,
                              "bg-green-100 text-green-800": !isUser && !isTool,
                              "bg-yellow-100 text-yellow-800": isTool,
                            }
                          )}>
                            {isUser ? "You" : isTool ? "Tool" : "AI"}
                          </span>
                          <span className="text-xs text-muted-foreground">
                            {new Date(message.timestamp).toLocaleTimeString()}
                          </span>
                        </div>
                        <p className="text-sm whitespace-pre-wrap break-words">
                          {message.content}
                        </p>
                        {message.metadata && (
                          <div className="mt-2 p-2 bg-gray-100 rounded text-xs">
                            <strong>Additional Info:</strong>
                            <div className="mt-1 space-y-1">
                              {Object.entries(message.metadata).map(([key, value]) => (
                                <div key={key} className="flex justify-between">
                                  <span className="text-gray-600 capitalize">
                                    {key.replace(/_/g, ' ')}:
                                  </span>
                                  <span className="font-medium">
                                    {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                                  </span>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    );
                  })
                )}
              </div>
            </div>
            
            <div className="flex justify-end gap-2 p-6 border-t">
              <Button variant="outline" onClick={() => setShowHistoryPopup(false)}>
                <XIcon className="h-4 w-4 mr-2" />
                Close
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
