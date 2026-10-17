import type { AgentEvent, ChatEvent, ChatTurn, Conversation } from "./types";

export type ChatState = {
  conversations: Conversation[];
  activeConversationId: string | null;
};

export const initialChatState: ChatState = {
  conversations: [],
  activeConversationId: null,
};

export function chatReducer(state: ChatState, event: ChatEvent): ChatState {
  switch (event.type) {
    case "select":
      return { ...state, activeConversationId: event.conversationId };

    case "turn-start": {
      const existing = state.conversations.find((chat) => chat.id === event.conversationId);
      const conversation: Conversation = existing
        ? {
            ...existing,
            turns: [...existing.turns, event.user, event.assistant],
            updatedAt: event.at,
            isLoading: true,
            error: undefined,
          }
        : {
            id: event.conversationId,
            title: titleFromMessage(event.user.content),
            createdAt: event.at,
            updatedAt: event.at,
            turns: [event.user, event.assistant],
            isLoading: true,
          };

      return {
        activeConversationId: event.conversationId,
        conversations: [conversation, ...state.conversations.filter((chat) => chat.id !== event.conversationId)],
      };
    }

    case "loading":
      return updateConversation(state, event.conversationId, (chat) => ({
        ...chat,
        isLoading: event.isLoading,
      }));

    case "agent-event":
      return updateConversation(state, event.conversationId, (chat) => ({
        ...chat,
        turns: appendAgentEvent(chat.turns, event.assistantId, event.event),
      }));

    case "error":
      return updateConversation(state, event.conversationId, (chat) => ({
        ...chat,
        isLoading: false,
        error: event.message,
      }));
  }
}

function updateConversation(
  state: ChatState,
  id: string,
  update: (conversation: Conversation) => Conversation,
): ChatState {
  return {
    ...state,
    conversations: state.conversations.map((chat) => (chat.id === id ? update(chat) : chat)),
  };
}

function titleFromMessage(message: string): string {
  const firstLine = message.replace(/\s+/g, " ").trim();
  return firstLine.length > 48 ? `${firstLine.slice(0, 47).trimEnd()}…` : firstLine;
}

function appendAgentEvent(turns: ChatTurn[], assistantId: string, event: AgentEvent): ChatTurn[] {
  return turns.map((turn) =>
    turn.id === assistantId ? { ...turn, events: [...turn.events, event] } : turn,
  );
}
