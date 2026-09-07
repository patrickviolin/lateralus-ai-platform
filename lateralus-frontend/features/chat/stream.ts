import type { StreamEventEnvelope, WeatherPayload } from "./types";

export type ParsedSseEvent = {
  event?: string;
  data: StreamEventEnvelope;
};

export async function* parseAgentStream(
  body: ReadableStream<Uint8Array>,
): AsyncGenerator<ParsedSseEvent> {
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
        if (parsed) {
          yield parsed;
        }
      }

      if (done) {
        if (buffer.trim()) {
          const parsed = parseSseFrame(buffer);
          if (parsed) {
            yield parsed;
          }
        }
        break;
      }
    }
  } finally {
    reader.releaseLock();
  }
}

export function parseSseFrame(frame: string): ParsedSseEvent | null {
  const eventLines = frame.split(/\r?\n/);
  const event = eventLines
    .find((line) => line.startsWith("event:"))
    ?.slice("event:".length)
    .trim();
  const data = eventLines
    .filter((line) => line.startsWith("data:"))
    .map((line) => line.slice("data:".length).trimStart())
    .join("\n");

  if (!data) {
    return null;
  }

  return {
    event,
    data: JSON.parse(data) as StreamEventEnvelope,
  };
}

export function parseWeatherPayload(value: unknown): WeatherPayload | undefined {
  const parsed = parseJsonIfString(value);

  if (isRecord(parsed) && "content" in parsed) {
    return parseWeatherPayload(parsed.content);
  }

  if (!isRecord(parsed)) {
    return undefined;
  }

  return {
    city: typeof parsed.city === "string" ? parsed.city : undefined,
    temp_c: typeof parsed.temp_c === "number" ? parsed.temp_c : undefined,
    condition:
      typeof parsed.condition === "string" ? parsed.condition : undefined,
    summary: typeof parsed.summary === "string" ? parsed.summary : undefined,
  };
}

export function formatWeatherJson(value: unknown): WeatherPayload | undefined {
  const payload = parseWeatherPayload(value);

  if (!payload) {
    return undefined;
  }

  return {
    city: payload.city,
    temp_c: payload.temp_c,
    condition: payload.condition,
  };
}

export function parseJsonIfString(value: unknown): unknown {
  if (typeof value !== "string") {
    return value;
  }

  try {
    return JSON.parse(value);
  } catch {
    return value;
  }
}

export function extractCity(value: unknown): string | undefined {
  const parsed = parseJsonIfString(value);

  if (isRecord(parsed) && typeof parsed.city === "string") {
    return parsed.city;
  }

  return undefined;
}

export function extractText(value: unknown): string {
  if (typeof value === "string") {
    return normalizeText(value);
  }

  if (!isRecord(value)) {
    return "";
  }

  if (typeof value.content === "string") {
    return normalizeText(value.content);
  }

  if (Array.isArray(value.content)) {
    return value.content
      .map((item) => {
        if (typeof item === "string") {
          return normalizeText(item);
        }
        if (isRecord(item) && typeof item.text === "string") {
          return normalizeText(item.text);
        }
        return "";
      })
      .join("");
  }

  return "";
}

export function isWeatherJsonFragment(value: string): boolean {
  const trimmedValue = value.trimStart();

  return (
    trimmedValue.startsWith("{") ||
    trimmedValue.includes('"city"') ||
    trimmedValue.includes('"temp_c"') ||
    trimmedValue.includes('"condition"') ||
    trimmedValue.includes('"summary"')
  );
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function normalizeText(value: string): string {
  const parsed = parseJsonIfString(value);

  if (isRecord(parsed) && typeof parsed.summary === "string") {
    return parsed.summary;
  }

  return value;
}
