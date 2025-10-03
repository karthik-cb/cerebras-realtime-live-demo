import AutoScrollToBottom from "@/components/AutoScrollToBottom";
import ChatMessage from "@/components/ChatMessage";
import LiveMessages from "@/components/LiveMessages";
import ConversationMetricsSummary from "@/components/ConversationMetricsSummary";
import { useAppState } from "@/hooks/useAppState";
import { Message, normalizeMessageText } from "@/lib/messages";
import { RTVIEvent } from "@pipecat-ai/client-js";
import { useRTVIClientEvent } from "@pipecat-ai/client-react";
import { useCallback, useState } from "react";

interface Props {
  autoscroll?: boolean;
  messages: Message[];
  conversation?: {
    metrics_summary?: {
      total_messages: number;
      total_latency: number;
      total_tokens: number;
      service_breakdown: {
        stt: { count: number; total_latency: number; avg_latency: number };
        llm: { count: number; total_latency: number; avg_latency: number; total_tokens: number };
        tts: { count: number; total_latency: number; avg_latency: number; total_characters: number };
      };
    };
  } | null;
}

export default function ChatMessages({ autoscroll = true, messages, conversation }: Props) {
  const { conversationId } = useAppState();
  const [isBotSpeaking, setIsBotSpeaking] = useState(false);

  console.log("💬 ChatMessages:", { conversationId, messageCount: messages.length });

  useRTVIClientEvent(
    RTVIEvent.BotStartedSpeaking,
    useCallback(() => {
      setIsBotSpeaking(true);
    }, []),
  );
  useRTVIClientEvent(
    RTVIEvent.BotStoppedSpeaking,
    useCallback(() => {
      setIsBotSpeaking(false);
    }, []),
  );
  useRTVIClientEvent(
    RTVIEvent.Disconnected,
    useCallback(() => {
      setIsBotSpeaking(false);
      // Trigger conversation metrics generation when disconnected
      if (conversationId) {
        console.log("📊 Conversation ended, metrics should be generated automatically");
        // The backend will automatically generate metrics when the conversation ends
        // We could also trigger a refresh here if needed
      }
    }, [conversationId]),
  );

  return (
    <div className="flex flex-col gap-4">
      {/* Conversation Metrics Summary */}
      {conversation?.metrics_summary && (
        <ConversationMetricsSummary metrics={conversation.metrics_summary} />
      )}
      
      {messages
        .filter((m) => m.content.role !== "system")
        .filter((m) => normalizeMessageText(m).trim() !== "")
        .map((message, index) => (
          <ChatMessage
            key={index}
            isSpeaking={
              message.content.role === "assistant" &&
              index === messages.length - 1 &&
              isBotSpeaking
            }
            message={message}
          />
        ))}
      <LiveMessages
        autoscroll={autoscroll}
        conversationId={conversationId}
        isBotSpeaking={isBotSpeaking}
        messages={messages}
      />
      <AutoScrollToBottom />
    </div>
  );
}
