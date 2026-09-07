export const EVENTS = [
  "on_chat_model_start",
  "on_chat_model_stream",
  "on_chat_model_end",
  "on_tool_start",
  "on_tool_end",
] as const;

export type EventType = (typeof EVENTS)[number];

export type WeatherPayload = {
  city?: string;
  temp_c?: number;
  condition?: string;
};

export type ToolCall = {
  name: string;
  args: Record<string, unknown>;
  id?: string;
};

export type LcMessage = {
  lc?: number;
  type?: string;
  id?: string[];
  content?: unknown;
  kwargs?: {
    content?: unknown;
    type?: string;
    name?: string;
    tool_calls?: ToolCall[];
  };
};

export type StreamEventEnvelope = {
  event?: string;
  name?: string;
  run_id?: string;
  data?: {
    input?: unknown;
    output?: unknown;
    chunk?: unknown;
    [key: string]: unknown;
  };
  [key: string]: unknown;
};

export type AgentEvent = {
  type: EventType;
  data: StreamEventEnvelope;
  at: number;
};

export type ChatTurn = {
  id: string;
  role: "user" | "assistant";
  content: string;
  events: AgentEvent[];
};

export type ChatEvent =
  | { type: "reset" }
  | { type: "loading"; isLoading: boolean }
  | { type: "turn-start"; user: ChatTurn; assistant: ChatTurn }
  | { type: "agent-event"; assistantId: string; event: AgentEvent }
  | { type: "error"; message: string };

export class UnknownEventError extends Error {
  constructor(type: string) {
    super(`unknown event type: ${type}`);
    this.name = "UnknownEventError";
  }
}

export function isEventType(type: string): type is EventType {
  return (EVENTS as readonly string[]).includes(type);
}
