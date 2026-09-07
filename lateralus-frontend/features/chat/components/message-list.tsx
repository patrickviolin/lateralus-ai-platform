import type { ChatMessage, ToolCallState } from "../types";
import { ModelRenderer } from "../renderers/model-renderer";
import { ToolRenderer } from "../renderers/tool-renderer";

type MessageListProps = {
  messages: ChatMessage[];
  toolCall?: ToolCallState;
  isLoading: boolean;
  error?: string;
};

export function MessageList({
  messages,
  toolCall,
  isLoading,
  error,
}: MessageListProps) {
  if (messages.length === 0 && !toolCall) {
    return null;
  }

  const hasAssistantText = messages.some(
    (message) => message.role === "assistant" && message.content.trim(),
  );
  const shouldShowThinking =
    isLoading && (!toolCall || (toolCall.status === "complete" && !hasAssistantText));

  return (
    <div className="mx-auto flex w-[min(92vw,900px)] flex-1 flex-col gap-8 px-4 pb-40 pt-24">
      {messages.map((message, index) => (
        <div key={message.id} className="contents">
          {message.role === "user" ? (
            <div className="flex justify-end">
              <div className="max-w-[70%] rounded-2xl bg-[#111827] px-6 py-4 text-lg text-slate-100 shadow-[0_16px_48px_rgba(0,0,0,0.25)]">
                {message.content}
              </div>
            </div>
          ) : (
            <ModelRenderer content={message.content} />
          )}

          {index === 0 && toolCall ? <ToolRenderer toolCall={toolCall} /> : null}
        </div>
      ))}

      {shouldShowThinking ? <ThinkingIndicator /> : null}

      {error ? (
        <div className="rounded-2xl border border-red-400/20 bg-red-500/10 px-5 py-4 text-sm text-red-200">
          {error}
        </div>
      ) : null}
    </div>
  );
}

function ThinkingIndicator() {
  return (
    <div className="relative ml-2 flex items-center gap-6 pt-8">
      <span className="size-2.5 rounded-full bg-sky-300 shadow-[0_0_18px_rgba(125,211,252,0.9)]" />
      <span className="thinking-shimmer text-xl text-slate-400">
        Pensando...
      </span>
    </div>
  );
}
