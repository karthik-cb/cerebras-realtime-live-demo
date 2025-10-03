import { Message } from "@/lib/messages";

export interface ConversationModel {
  conversation_id: string;
  title?: string | null;
  created_at: string;
  updated_at: string;
  messages?: Message[];
  metrics_summary?: ConversationMetricsSummary;
}

interface GetConversationsParams {
  page: number;
  searchQuery?: string;
}

const PAGE_SIZE = 20;

export async function getConversations({
  page,
  searchQuery = "",
}: GetConversationsParams) {
  const params = new URLSearchParams();
  params.append("page", String(page));
  params.append("per_page", String(PAGE_SIZE));
  if (searchQuery) params.append("q", searchQuery.trim());
  try {
    const response = await fetch(
      `${import.meta.env.VITE_SERVER_URL}/conversations?${params.toString()}`,
    );
    if (response.ok) {
      return (await response.json()) as ConversationModel[];
    }
    return [];
  } catch (e) {
    console.error(e);
    return [];
  }
}

interface ConversationMetricsSummary {
  total_messages: number;
  total_latency: number;
  total_tokens: number;
  service_breakdown: {
    stt: { count: number; total_latency: number; avg_latency: number };
    llm: { count: number; total_latency: number; avg_latency: number; total_tokens: number };
    tts: { count: number; total_latency: number; avg_latency: number; total_characters: number };
    mcp: { count: number; total_latency: number; avg_latency: number };
  };
}

interface GetConversationAndMessagesResponse {
  conversation: ConversationModel;
  messages: Message[];
  metrics_summary: ConversationMetricsSummary;
}

export async function getConversation(conversationId: string) {
  try {
    const response = await fetch(
      `${
        import.meta.env.VITE_SERVER_URL
      }/conversations/${conversationId}/messages`,
    );
    if (response.ok) {
      const json =
        (await response.json()) as GetConversationAndMessagesResponse;
      const conversation: ConversationModel = {
        ...json.conversation,
        messages: json.messages,
        metrics_summary: json.metrics_summary,
      };
      return conversation;
    }
    return null;
  } catch (e) {
    console.error(e);
    return null;
  }
}
