import type { ChatEvent, ChatMessage, ToolCallState } from "./types";

export type ChatState = {
  messages: ChatMessage[];
  toolCall?: ToolCallState;
  isLoading: boolean;
  error?: string;
};

export const initialChatState: ChatState = {
  messages: [],
  isLoading: false,
};

export function chatReducer(state: ChatState, event: ChatEvent): ChatState {
  switch (event.type) {
    case "reset":
      return initialChatState;
    case "loading":
      return {
        ...state,
        isLoading: event.isLoading,
      };
    case "message":
      return {
        ...state,
        messages: [...state.messages, event.message],
        isLoading: true,
        error: undefined,
      };
    case "assistant-delta":
      return appendAssistantContent(state, event.content);
    case "tool-start":
      return {
        ...state,
        toolCall: event.tool,
        isLoading: true,
      };
    case "tool-end":
      if (!state.toolCall) {
        return state;
      }

      return {
        ...state,
        toolCall: {
          ...state.toolCall,
          status: "complete",
          durationSeconds: event.durationSeconds,
          payload: event.payload,
          rawJson: event.rawJson,
        },
        isLoading: true,
      };
    case "error":
      return {
        ...state,
        isLoading: false,
        error: event.message,
      };
    default:
      return state;
  }
}

function appendAssistantContent(state: ChatState, content: string): ChatState {
  if (!content) {
    return state;
  }

  const messages = [...state.messages];
  const lastMessage = messages.at(-1);

  if (lastMessage?.role === "assistant") {
    messages[messages.length - 1] = {
      ...lastMessage,
      content: `${lastMessage.content}${content}`,
    };
  } else {
    messages.push({
      id: crypto.randomUUID(),
      role: "assistant",
      content,
    });
  }

  return {
    ...state,
    messages,
  };
}
