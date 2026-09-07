export type WeatherPayload = {
  city?: string;
  temp_c?: number;
  condition?: string;
  summary?: string;
};

export type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
};

export type ToolCallState = {
  id: string;
  name: string;
  city?: string;
  status: "called" | "running" | "complete" | "error";
  startedAt: number;
  durationSeconds?: number;
  payload?: WeatherPayload;
  rawJson?: unknown;
};

export type ChatEvent =
  | { type: "reset" }
  | { type: "loading"; isLoading: boolean }
  | { type: "message"; message: ChatMessage }
  | { type: "assistant-delta"; content: string }
  | { type: "tool-start"; tool: ToolCallState }
  | {
      type: "tool-end";
      id?: string;
      payload?: WeatherPayload;
      rawJson?: unknown;
      durationSeconds?: number;
    }
  | { type: "error"; message: string };

export type StreamEventEnvelope = {
  event?: string;
  name?: string;
  run_id?: string;
  data?: {
    input?: unknown;
    output?: unknown;
    chunk?: unknown;
  };
};
