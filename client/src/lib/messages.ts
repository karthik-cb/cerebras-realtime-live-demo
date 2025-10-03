import { LLMMessageRole } from "@/lib/llm";

export interface TextContent {
  type: "text";
  text: string;
}

export interface ImageContent {
  type: "image_url";
  image_url: {
    url: string;
  };
}

export interface InteractionMetrics {
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

export interface Message {
  created_at: string;
  content: {
    role: LLMMessageRole;
    content: string | Array<TextContent | ImageContent>;
  };
  conversation_id: string;
  extra_metadata: Record<string, unknown> | null;
  message_id: string;
  message_number: number;
  updated_at: string;
  metrics?: InteractionMetrics[];
}

export const addNewLinesBeforeCodeblocks = (markdown: string) => {
  if (!markdown || typeof markdown !== 'string') {
    return markdown || '';
  }
  return markdown.match(/([^\n])(\n```)/)
    ? markdown.replace(/([^\n])(\n```)/g, "$1\n$2")
    : markdown;
};

export function normalizeMessageText(message: Message) {
  try {
    const content = Array.isArray(message.content.content)
      ? message.content.content
          .filter((tc) => tc.type === "text")
          .map((tc) => tc.text)
          .join(" ")
      : message.content.content;
    
    return addNewLinesBeforeCodeblocks(content || '');
  } catch (error) {
    console.error('Error normalizing message text:', error, message);
    return '';
  }
}

export function extractMessageImages(message: Message) {
  return Array.isArray(message.content.content)
    ? message.content.content
        .filter((t) => t.type === "image_url")
        .map((t) => t.image_url.url)
    : [];
}
