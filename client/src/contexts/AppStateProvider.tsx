import {
  AppStateContext,
  ConversationType,
  InteractionMode,
  ModelPreferences,
  ModelOption,
} from "@/contexts/AppStateContext";
import { useConversation } from "@/hooks/useConversation";
import { useDeferredValue, useEffect, useState } from "react";

const C = "c";
const Q = "q";

interface Props {
  websocketEnabled: boolean;
  webrtcEnabled: boolean;
  availableModels?: {
    stt: ModelOption[];
    llm: ModelOption[];
    tts: ModelOption[];
    mcp: ModelOption[];
  };
}

export const AppStateProvider: React.FC<React.PropsWithChildren<Props>> = ({
  children,
  webrtcEnabled,
  websocketEnabled,
  availableModels: initialAvailableModels,
}) => {
  const searchParams = new URLSearchParams(location.search);
  const cid = searchParams.get(C);
  const q = searchParams.get(Q);

  const [conversationId, setConversationId] = useState(cid ?? "");
  const [interactionMode, setInteractionMode] =
    useState<InteractionMode>("informational");
  const [conversationType, setConversationType] = useState<ConversationType>(
    cid ? "text-voice" : null,
  );

  useEffect(() => {
    console.log("🔄 AppStateProvider useEffect triggered:", {
      conversationId,
      conversationType,
      url: window.location.href
    });
    
    // Only auto-set conversation type if we're not explicitly in voice-to-voice mode
    // This allows voice-to-voice conversations to maintain their conversation ID and type
    if (conversationId && conversationType !== "voice-to-voice") {
      console.log("✅ Setting conversationType to 'text-voice'");
      setConversationType("text-voice");
    } else if (!conversationId && conversationType !== "voice-to-voice") {
      console.log("✅ Setting conversationType to null");
      setConversationType(null);
    } else {
      console.log("✅ Preserving voice-to-voice mode, no change to conversationType");
    }
    // If we're in voice-to-voice mode, don't change the conversation type regardless of conversationId
  }, [conversationId]);

  const [searchQuery, setSearchQuery] = useState(q ?? "");
  const deferredSearchQuery = useDeferredValue(searchQuery);

  // Model preferences state
  const [modelPreferences, setModelPreferences] = useState<ModelPreferences>({
    stt: "nova-2-general",
    llm: "gpt-oss-120b",
    tts: "aura-luna-en",
    mcp: ["filesystem"],
  });

  const [availableModels, setAvailableModels] = useState<{
    stt: ModelOption[];
    llm: ModelOption[];
    tts: ModelOption[];
    mcp: ModelOption[];
  }>(initialAvailableModels || {
    stt: [],
    llm: [],
    tts: [],
    mcp: [],
  });

  const { conversation, isFetched } = useConversation(conversationId);

  useEffect(() => {
    if (isFetched && !conversation) {
      setConversationId("");
    }
  }, [conversation, isFetched]);

  useEffect(() => {
    const searchParams = new URLSearchParams();
    if (conversationId) searchParams.append(C, conversationId);
    if (searchQuery) searchParams.append(Q, searchQuery);
    history.replaceState(null, "", `/?${searchParams.toString()}`);
  }, [conversationId, searchQuery]);

  return (
    <AppStateContext.Provider
      value={{
        conversationId,
        setConversationId,
        conversationType,
        setConversationType,
        interactionMode,
        setInteractionMode,
        searchQuery: deferredSearchQuery,
        setSearchQuery,
        webrtcEnabled,
        websocketEnabled,
        modelPreferences,
        setModelPreferences,
        availableModels,
        setAvailableModels,
      }}
    >
      {children}
    </AppStateContext.Provider>
  );
};
