import {
  cityOf,
  messageText,
  messageToolCalls,
  parseWeatherPayload,
} from "./stream";
import { UnknownEventError, type AgentEvent, type WeatherPayload } from "./types";

export type TextBlock = {
  kind: "text";
  id: string;
  text: string;
  streaming: boolean;
};

export type ToolBlock = {
  kind: "tool";
  id: string;
  name: string;
  input: unknown;
  output?: unknown;
  payload?: WeatherPayload;
  status: "running" | "done";
  startedAt?: number;
  endedAt?: number;
};

export type Block = TextBlock | ToolBlock;

export function foldEvents(events: AgentEvent[]): Block[] {
  const blocks: Block[] = [];
  events.forEach((event, index) => applyEvent(blocks, event, index));
  return blocks;
}

export function isThinking(blocks: Block[]): boolean {
  const last = blocks.at(-1);
  if (!last) return true;
  if (last.kind === "tool") return last.status === "done";
  return last.streaming && last.text.length === 0;
}

export function toolCity(block: ToolBlock): string {
  return block.payload?.city ?? cityOf(block.input) ?? "cidade";
}

function applyEvent(blocks: Block[], event: AgentEvent, index: number) {
  const id = String(event.data.run_id ?? `evt-${index}`);

  switch (event.type) {
    case "on_chat_model_start":
      blocks.push({ kind: "text", id, text: "", streaming: true });
      return;

    case "on_chat_model_stream": {
      const piece = messageText(event.data.data?.chunk);
      if (!piece) return;
      const open = openText(blocks) ?? pushText(blocks, id);
      open.text += piece;
      return;
    }

    case "on_chat_model_end": {
      const open = openText(blocks);
      if (!open) return;

      const output = event.data.data?.output;
      if (messageToolCalls(output).length > 0) {
        blocks.splice(blocks.indexOf(open), 1);
        return;
      }

      open.text = messageText(output) || open.text;
      open.streaming = false;
      return;
    }

    case "on_tool_start":
      blocks.push({
        kind: "tool",
        id,
        name: event.data.name ?? "tool",
        input: event.data.data?.input,
        status: "running",
        startedAt: event.at,
      });
      return;

    case "on_tool_end": {
      const tool = findTool(blocks, id) ?? lastRunningTool(blocks);
      if (!tool) return;
      tool.output = event.data.data?.output;
      tool.payload = parseWeatherPayload(event.data.data?.output);
      tool.status = "done";
      tool.endedAt = event.at;
      return;
    }

    default:
      throw new UnknownEventError((event as { type: string }).type);
  }
}

function openText(blocks: Block[]): TextBlock | undefined {
  for (let i = blocks.length - 1; i >= 0; i--) {
    const block = blocks[i];
    if (block.kind === "text") return block.streaming ? block : undefined;
  }
  return undefined;
}

function pushText(blocks: Block[], id: string): TextBlock {
  const block: TextBlock = { kind: "text", id, text: "", streaming: true };
  blocks.push(block);
  return block;
}

function findTool(blocks: Block[], id: string): ToolBlock | undefined {
  return blocks.find((block): block is ToolBlock => {
    return block.kind === "tool" && block.id === id;
  });
}

function lastRunningTool(blocks: Block[]): ToolBlock | undefined {
  for (let i = blocks.length - 1; i >= 0; i--) {
    const block = blocks[i];
    if (block.kind === "tool" && block.status === "running") return block;
  }
  return undefined;
}
