import {
  isEventType,
  UnknownEventError,
  type AgentEvent,
  type LcMessage,
  type StreamEventEnvelope,
  type ToolCall,
  type WeatherPayload,
} from "./types";

export async function* parseAgentStream(
  body: ReadableStream<Uint8Array>,
): AsyncGenerator<AgentEvent> {
  const reader = body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  try {
    while (true) {
      const { value, done } = await reader.read();
      buffer += decoder.decode(value, { stream: !done });

      const frames = buffer.split(/\r?\n\r?\n/);
      buffer = frames.pop() ?? "";

      for (const frame of frames) {
        const parsed = parseSseFrame(frame);
        if (parsed) yield parsed;
      }

      if (done) {
        if (buffer.trim()) {
          const parsed = parseSseFrame(buffer);
          if (parsed) yield parsed;
        }
        break;
      }
    }
  } finally {
    reader.releaseLock();
  }
}

export function parseSseFrame(frame: string): AgentEvent | null {
  let type = "";
  const dataLines: string[] = [];

  for (const line of frame.split(/\r?\n/)) {
    if (line.startsWith("event:")) type = line.slice("event:".length).trim();
    if (line.startsWith("data:")) {
      dataLines.push(line.slice("data:".length).trimStart());
    }
  }

  if (!type || dataLines.length === 0) return null;
  if (!isEventType(type)) throw new UnknownEventError(type);

  return {
    type,
    data: JSON.parse(dataLines.join("\n")) as StreamEventEnvelope,
    at: Date.now(),
  };
}

export function parseWeatherPayload(value: unknown): WeatherPayload | undefined {
  const parsed = parseJsonIfString(messageText(value));

  if (!isRecord(parsed)) return undefined;

  return {
    city: typeof parsed.city === "string" ? parsed.city : undefined,
    temp_c: typeof parsed.temp_c === "number" ? parsed.temp_c : undefined,
    condition: typeof parsed.condition === "string" ? parsed.condition : undefined,
  };
}

export function parseJsonIfString(value: unknown): unknown {
  if (typeof value !== "string") return value;

  try {
    return JSON.parse(value);
  } catch {
    return value;
  }
}

export function cityOf(input: unknown): string | undefined {
  const parsed = parseJsonIfString(input);
  if (!isRecord(parsed)) return undefined;
  return typeof parsed.city === "string" ? parsed.city : undefined;
}

export function messageText(message: unknown): string {
  const direct = contentText(message);
  if (direct) return direct;

  const lcMessage = asMessage(message);
  if (!lcMessage) return "";
  if (lcMessage.kwargs && "content" in lcMessage.kwargs) {
    return contentText(lcMessage.kwargs.content);
  }
  return contentText(lcMessage.content);
}

export function messageToolCalls(message: unknown): ToolCall[] {
  const calls = asMessage(message)?.kwargs?.tool_calls;
  return Array.isArray(calls) ? calls : [];
}

export function formatJson(value: unknown): string {
  const parsed = parseJsonIfString(messageText(value));
  if (typeof parsed === "string") return parsed;
  return JSON.stringify(parsed, null, 2);
}

function contentText(content: unknown): string {
  if (typeof content === "string") return content;
  if (!Array.isArray(content)) return "";

  return content
    .map((block) => {
      if (typeof block === "string") return block;
      if (isRecord(block) && typeof block.text === "string") return block.text;
      return "";
    })
    .join("");
}

function asMessage(value: unknown): LcMessage | undefined {
  if (!isRecord(value)) return undefined;
  return value as LcMessage;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}
