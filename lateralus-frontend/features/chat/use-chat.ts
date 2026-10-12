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
  const threadId = useRef<string | null>(null);

  const newChat = useCallback(() => {
    activeController.current?.abort();
    activeController.current = null;
    threadId.current = null;
    dispatch({ type: "reset" });
  }, []);

  const sendMessage = useCallback(async (message: string) => {
    const trimmedMessage = message.trim();
    if (!trimmedMessage) return;

    activeController.current?.abort();
    const controller = new AbortController();
    activeController.current = controller;
    threadId.current ??= uid();
    const currentThreadId = threadId.current;

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
      const body = await executeAgent(trimmedMessage, currentThreadId, controller.signal);

      for await (const event of parseAgentStream(body)) {
        if (activeController.current !== controller) break;
        dispatch({
          type: "agent-event",
          assistantId: assistant.id,
          event,
        });
      }
    } catch (error) {
      if (!controller.signal.aborted && activeController.current === controller) {
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
        dispatch({ type: "loading", isLoading: false });
      }
    }
  }, []);

  return {
    ...state,
    sendMessage,
    newChat,
  };
}
