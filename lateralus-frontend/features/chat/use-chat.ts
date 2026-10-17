"use client";

import { useCallback, useEffect, useReducer, useRef } from "react";

import { executeAgent } from "./api";
import { chatReducer, initialChatState } from "./reducer";
import { parseAgentStream } from "./stream";
import type { ChatTurn } from "./types";

function uid() {
  return crypto.randomUUID();
}

export function useChat() {
  const [state, dispatch] = useReducer(chatReducer, initialChatState);
  const controllers = useRef(new Map<string, AbortController>());
  const activeConversationId = useRef<string | null>(null);

  useEffect(() => {
    const pending = controllers.current;
    return () => {
      for (const controller of pending.values()) controller.abort();
      pending.clear();
    };
  }, []);

  const newChat = useCallback(() => {
    activeConversationId.current = null;
    dispatch({ type: "select", conversationId: null });
  }, []);

  const selectConversation = useCallback((conversationId: string) => {
    if (conversationId === activeConversationId.current) return;
    activeConversationId.current = conversationId;
    dispatch({ type: "select", conversationId });
  }, []);

  const sendMessage = useCallback(async (message: string) => {
    const trimmedMessage = message.trim();
    if (!trimmedMessage) return;

    const conversationId = activeConversationId.current ?? uid();
    if (controllers.current.has(conversationId)) return;
    const controller = new AbortController();
    controllers.current.set(conversationId, controller);
    activeConversationId.current = conversationId;

    const user: ChatTurn = {
      id: uid(),
      role: "user",
      content: trimmedMessage,
      events: [],
    };
    const assistant: ChatTurn = {
      id: uid(),
      role: "assistant",
      content: "",
      events: [],
    };

    dispatch({ type: "turn-start", conversationId, user, assistant, at: Date.now() });

    try {
      const body = await executeAgent(trimmedMessage, conversationId, controller.signal);

      for await (const event of parseAgentStream(body)) {
        if (controllers.current.get(conversationId) !== controller) break;
        dispatch({ type: "agent-event", conversationId, assistantId: assistant.id, event });
      }
    } catch (error) {
      if (!controller.signal.aborted && controllers.current.get(conversationId) === controller) {
        dispatch({
          type: "error",
          conversationId,
          message:
            error instanceof Error
              ? error.message
              : "Unexpected error while calling the agent",
        });
      }
    } finally {
      if (controllers.current.get(conversationId) === controller) {
        controllers.current.delete(conversationId);
        dispatch({ type: "loading", conversationId, isLoading: false });
      }
    }
  }, []);

  const activeConversation = state.conversations.find((chat) => chat.id === state.activeConversationId);

  return {
    conversations: state.conversations,
    activeConversationId: state.activeConversationId,
    turns: activeConversation?.turns ?? [],
    isLoading: activeConversation?.isLoading ?? false,
    error: activeConversation?.error,
    sendMessage,
    newChat,
    selectConversation,
  };
}
