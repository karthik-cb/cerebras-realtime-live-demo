import { getConversation } from "@/lib/conversations";
import { useQuery, useQueryClient } from "@tanstack/react-query";

export const useConversation = (conversationId: string) => {
  const { data: conversation, ...query } = useQuery({
    queryKey: ["conversation", conversationId],
    queryFn: async () => {
      console.log("📞 useConversation queryFn called:", { conversationId });
      if (!conversationId) {
        console.log("❌ No conversationId provided");
        return null;
      }
      const result = await getConversation(conversationId);
      console.log("📞 useConversation result:", { 
        conversationId, 
        hasConversation: !!result,
        messageCount: result?.messages?.length || 0
      });
      return result;
    },
  });
  const queryClient = useQueryClient();
  const invalidate = () =>
    queryClient.invalidateQueries({
      queryKey: ["conversation", conversationId],
    });
  return {
    conversation,
    ...query,
    invalidate,
  };
};
