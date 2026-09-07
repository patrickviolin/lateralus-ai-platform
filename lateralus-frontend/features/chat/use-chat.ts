"use client";

import { useCallback, useReducer, useRef } from "react";

import { executeAgent } from "./api";
import { chatReducer, initialChatState } from "./reducer";
import {
  extractCity,
  extractText,
  formatWeatherJson,
  isWeatherJsonFragment,
  parseAgentStream,
  parseJsonIfString,
  parseWeatherPayload,
} from "./stream";
import type { ToolCallState } from "./types";

export function useChat() {
  const [state, dispatch] = useReducer(chatReducer, initialChatState);
  const activeController = useRef<AbortController | null>(null);
  const activeTool = useRef<ToolCallState | null>(null);
  const receivedAssistantStream = useRef(false);
  const ignoringStructuredStream = useRef(false);

  const newChat = useCallback(() => {
    activeController.current?.abort();
    activeController.current = null;
    activeTool.current = null;
    receivedAssistantStream.current = false;
    ignoringStructuredStream.current = false;
    dispatch({ type: "reset" });
  }, []);

  const sendMessage = useCallback(async (message: string) => {
    const trimmedMessage = message.trim();

    if (!trimmedMessage) {
      return;
    }

    activeController.current?.abort();
    const controller = new AbortController();
    activeController.current = controller;
    activeTool.current = null;
    receivedAssistantStream.current = false;
    ignoringStructuredStream.current = false;
    dispatch({ type: "loading", isLoading: true });

    dispatch({
      type: "message",
      message: {
        id: crypto.randomUUID(),
        role: "user",
        content: trimmedMessage,
      },
    });

    try {
      const body = await executeAgent(trimmedMessage, controller.signal);

      for await (const streamEvent of parseAgentStream(body)) {
        const eventName = streamEvent.event ?? streamEvent.data.event;
        const eventData = streamEvent.data.data;

        if (eventName === "on_tool_start") {
          const tool: ToolCallState = {
            id: streamEvent.data.run_id ?? crypto.randomUUID(),
            name: streamEvent.data.name ?? "get_weather",
            city: extractCity(eventData?.input),
            status: "running",
            startedAt: performance.now(),
          };

          activeTool.current = tool;
          dispatch({ type: "tool-start", tool });
        }

        if (eventName === "on_tool_end") {
          const rawJson = parseJsonIfString(eventData?.output);
          const durationSeconds = activeTool.current
            ? (performance.now() - activeTool.current.startedAt) / 1000
            : undefined;

          dispatch({
            type: "tool-end",
            id: streamEvent.data.run_id,
            payload: parseWeatherPayload(rawJson),
            rawJson: formatWeatherJson(rawJson),
            durationSeconds,
          });
        }

        if (eventName === "on_chat_model_stream") {
          const content = extractText(eventData?.chunk);
          ignoringStructuredStream.current ||= isWeatherJsonFragment(content);

          if (ignoringStructuredStream.current) {
            continue;
          }

          receivedAssistantStream.current ||= Boolean(content);

          await streamWords(content, controller.signal, (part) => {
            dispatch({
              type: "assistant-delta",
              content: part,
            });
          });
        }

        if (
          eventName === "on_chat_model_end" &&
          !receivedAssistantStream.current
        ) {
          await streamWords(
            extractText(eventData?.output),
            controller.signal,
            (part) => {
              dispatch({
                type: "assistant-delta",
                content: part,
              });
            },
          );
        }
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

async function streamWords(
  content: string,
  signal: AbortSignal,
  onWord: (part: string) => void,
) {
  const parts = content.match(/\S+\s*/g) ?? [];

  for (const part of parts) {
    if (signal.aborted) {
      return;
    }

    onWord(part);
    await wait(38);
  }
}

function wait(milliseconds: number) {
  return new Promise((resolve) => window.setTimeout(resolve, milliseconds));
}
