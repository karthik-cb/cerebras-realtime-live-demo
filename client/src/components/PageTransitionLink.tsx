import React from "react";
import { useAppState } from "@/hooks/useAppState";
import { cn } from "@/lib/utils";

interface Props extends React.AnchorHTMLAttributes<HTMLAnchorElement> {
  disabled?: boolean;
  href: string;
  customClickHandler?: () => void;
}

export const PageTransitionLink = React.forwardRef<HTMLAnchorElement, React.PropsWithChildren<Props>>(({
  className,
  disabled = false,
  href,
  onClick,
  customClickHandler,
  ...props
}, ref) => {
  const { setConversationId, setConversationType } = useAppState();

  const handleClick = (ev: React.MouseEvent<HTMLAnchorElement>) => {
    console.log("🔗 PageTransitionLink clicked:", {
      href,
      disabled,
      defaultPrevented: ev.defaultPrevented
    });
    
    if (disabled) return;
    
    // Call the onClick handler first (which might prevent default)
    onClick?.(ev);
    
    // If the onClick handler didn't prevent default, handle normally
    if (!ev.defaultPrevented) {
      console.log("✅ PageTransitionLink handling normally - setting conversationId:", href);
      ev.preventDefault();
      setConversationId(href);
      if (!href) setConversationType(null);
    } else {
      console.log("⏸️ PageTransitionLink default prevented by onClick handler");
    }
  };

  return (
    <a
      ref={ref}
      className={cn(className, {
        "cursor-pointer": !disabled,
        "cursor-not-allowed": disabled,
      })}
      href={`?c=${href}`}
      {...props}
      onClick={handleClick}
      tabIndex={disabled ? -1 : undefined}
    />
  );
});
