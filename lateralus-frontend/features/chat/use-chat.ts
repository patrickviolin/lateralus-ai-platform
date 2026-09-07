"use client";

import { useCallback, useReducer, useRef } from "react";

import { executeAgent } from "./api";
import { chatReducer, initialChatState } from "./reducer";
import { parseAgentStream } from "./stream";
import type { ChatTurn } from "./types";

function uid() {
  return crypto.randomUUID();
}

export function useChat() {
  const [state, dispatch] = useReducer(chatReducer, initialChatState);
  const activeController = useRef<AbortController | null>(null);

  const newChat = useCallback(() => {
    activeController.current?.abort();
    activeController.current = null;
    dispatch({ type: "reset" });
  }, []);

  const sendMessage = useCallback(async (message: string) => {
    const trimmedMessage = message.trim();
    if (!trimmedMessage) return;

    activeController.current?.abort();
    const controller = new AbortController();
    activeController.current = controller;

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

    dispatch({ type: "turn-start", user, assistant });

    try {
      const body = await executeAgent(trimmedMessage, controller.signal);

      for await (const event of parseAgentStream(body)) {
        dispatch({
          type: "agent-event",
          assistantId: assistant.id,
          event,
        });
      }
    } catch (error) {
      if (!controller.signal.aborted) {
        dispatch({
          type: "error",
          message:
            error instanceof Error
              ? error.message
              : "Unexpected error while calling the agent",
        });
      }
    } finally {
      if (activeController.current === controller) {
        activeController.current = null;
      }
      dispatch({ type: "loading", isLoading: false });
    }
  }, []);

  return {
    ...state,
    sendMessage,
    newChat,
  };
}
