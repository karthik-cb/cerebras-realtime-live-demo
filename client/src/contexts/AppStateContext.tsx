import { createContext, Dispatch, SetStateAction } from "react";

export type InteractionMode = "conversational" | "informational";

export type ConversationType = "voice-to-voice" | "text-voice" | null;

export interface ModelOption {
  id: string;
  name: string;
  description: string;
  provider: string;
  enabled: boolean;
}

export interface ModelPreferences {
  stt: string;
  llm: string;
  tts: string;
  mcp: string[];
}

interface AppStateContextValue {
  conversationId: string;
  setConversationId: Dispatch<SetStateAction<string>>;
  conversationType: ConversationType;
  setConversationType: Dispatch<SetStateAction<ConversationType>>;
  interactionMode: InteractionMode;
  setInteractionMode: Dispatch<SetStateAction<InteractionMode>>;
  searchQuery: string;
  setSearchQuery: Dispatch<SetStateAction<string>>;
  webrtcEnabled: boolean;
  websocketEnabled: boolean;
  modelPreferences: ModelPreferences;
  setModelPreferences: Dispatch<SetStateAction<ModelPreferences>>;
  availableModels: {
    stt: ModelOption[];
    llm: ModelOption[];
    tts: ModelOption[];
    mcp: ModelOption[];
  };
  setAvailableModels: Dispatch<SetStateAction<{
    stt: ModelOption[];
    llm: ModelOption[];
    tts: ModelOption[];
    mcp: ModelOption[];
  }>>;
}

const noop = () => {};

export const AppStateContext = createContext<AppStateContextValue>({
  conversationId: "",
  setConversationId: noop,
  conversationType: null,
  setConversationType: noop,
  interactionMode: "informational",
  setInteractionMode: noop,
  searchQuery: "",
  setSearchQuery: noop,
  webrtcEnabled: false,
  websocketEnabled: false,
  modelPreferences: {
    stt: "nova-2-general",
    llm: "gpt-oss-120b",
    tts: "aura-luna-en",
    mcp: ["filesystem"],
  },
  setModelPreferences: noop,
  availableModels: {
    stt: [],
    llm: [],
    tts: [],
    mcp: [],
  },
  setAvailableModels: noop,
});
