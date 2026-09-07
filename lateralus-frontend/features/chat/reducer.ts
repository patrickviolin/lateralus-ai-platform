import type { AgentEvent, ChatEvent, ChatTurn } from "./types";

export type ChatState = {
  turns: ChatTurn[];
  isLoading: boolean;
  error?: string;
};

export const initialChatState: ChatState = {
  turns: [],
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

    case "turn-start":
      return {
        ...state,
        turns: [...state.turns, event.user, event.assistant],
        isLoading: true,
        error: undefined,
      };

    case "agent-event":
      return {
        ...state,
        turns: appendAgentEvent(state.turns, event.assistantId, event.event),
      };

    case "error":
      return {
        ...state,
        isLoading: false,
        error: event.message,
      };
  }
}

function appendAgentEvent(
  turns: ChatTurn[],
  assistantId: string,
  event: AgentEvent,
): ChatTurn[] {
  return turns.map((turn) => {
    if (turn.id !== assistantId) return turn;
    return {
      ...turn,
      events: [...turn.events, event],
    };
  });
}
