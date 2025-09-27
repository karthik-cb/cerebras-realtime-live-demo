import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useAppState } from "@/hooks/useAppState";
import { useConversation } from "@/hooks/useConversation";
import { Message, normalizeMessageText } from "@/lib/messages";
import { cn } from "@/lib/utils";
import { HistoryIcon, XIcon } from "lucide-react";
import { useState } from "react";

interface Props {
  isOpen: boolean;
  onClose: () => void;
}

export function ConversationHistoryPopup({ isOpen, onClose }: Props) {
  const { conversationId } = useAppState();
  const { conversation, error } = useConversation(conversationId);
  const [selectedMessage, setSelectedMessage] = useState<number | null>(null);

  console.log("📋 ConversationHistoryPopup:", { conversationId, hasConversation: !!conversation, error });

  const messages = conversation?.messages ?? [];
  const visibleMessages = messages.filter((m) => m.content.role !== "system");

  const formatMessage = (message: Message) => {
    const text = normalizeMessageText(message);
    return text.trim();
  };

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[80vh] flex flex-col">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <HistoryIcon className="h-5 w-5" />
            Conversation History
          </DialogTitle>
          <DialogDescription>
            Review the text history of your conversation. Click on any message to copy it to clipboard.
          </DialogDescription>
        </DialogHeader>
        
        <ScrollArea className="flex-1 pr-4">
          <div className="space-y-4">
            {visibleMessages.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                No conversation history available yet.
              </div>
            ) : (
              visibleMessages.map((message, index) => {
                const isUser = message.content.role === "user";
                const isSelected = selectedMessage === index;
                const messageText = formatMessage(message);
                
                if (!messageText) return null;

                return (
                  <div
                    key={index}
                    className={cn(
                      "group relative p-4 rounded-lg border cursor-pointer transition-all hover:bg-muted/50",
                      {
                        "bg-muted border-primary": isSelected,
                        "bg-background border-border": !isSelected,
                        "ml-8": isUser,
                        "mr-8": !isUser,
                      }
                    )}
                    onClick={() => {
                      setSelectedMessage(isSelected ? null : index);
                      copyToClipboard(messageText);
                    }}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-2">
                          <span className={cn(
                            "text-xs font-medium px-2 py-1 rounded-full",
                            {
                              "bg-blue-100 text-blue-800": isUser,
                              "bg-green-100 text-green-800": !isUser,
                            }
                          )}>
                            {isUser ? "You" : "AI"}
                          </span>
                          <span className="text-xs text-muted-foreground">
                            {new Date(message.created_at).toLocaleTimeString()}
                          </span>
                        </div>
                        <p className="text-sm whitespace-pre-wrap break-words">
                          {messageText}
                        </p>
                      </div>
                      {isSelected && (
                        <div className="flex-shrink-0">
                          <span className="text-xs text-primary font-medium">
                            Copied!
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </ScrollArea>

        <div className="flex justify-end gap-2 pt-4 border-t">
          <Button variant="outline" onClick={onClose}>
            <XIcon className="h-4 w-4 mr-2" />
            Close
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
