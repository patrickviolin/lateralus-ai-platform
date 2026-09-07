import { foldEvents, isThinking } from "../blocks";
import { ModelRenderer } from "../renderers/model-renderer";
import { ToolRenderer } from "../renderers/tool-renderer";
import type { Block } from "../blocks";
import type { ChatTurn } from "../types";

type MessageListProps = {
  turns: ChatTurn[];
  isLoading: boolean;
  error?: string;
};

export function MessageList({ turns, isLoading, error }: MessageListProps) {
  const lastTurnId = turns.at(-1)?.id;

  return (
    <section className="mx-auto flex w-[min(92vw,780px)] flex-1 flex-col gap-7 px-4 pb-40 pt-8">
      {turns.map((turn) => {
        if (turn.role === "user") {
          return (
            <article key={turn.id} className="flex justify-end">
              <div className="max-w-[78%] whitespace-pre-wrap rounded-2xl rounded-br-md border border-white/10 bg-[#111827] px-5 py-3 text-base leading-7 text-slate-100">
                {turn.content}
              </div>
            </article>
          );
        }

        const blocks = foldEvents(turn.events);
        const live = isLoading && turn.id === lastTurnId;

        return (
          <article
            key={turn.id}
            className="grid grid-cols-[10px_minmax(0,1fr)] gap-4"
          >
            <span className="mt-3 size-2.5 rounded-full bg-cyan-300 shadow-[0_0_16px_rgba(103,232,249,0.65)]" />
            <div className="flex min-h-8 flex-col gap-3">
              {blocks.map(renderBlock)}
              {live && isThinking(blocks) ? <ThinkingIndicator /> : null}
            </div>
          </article>
        );
      })}

      {error ? (
        <div className="rounded-lg border border-red-400/30 bg-red-500/10 px-4 py-3 text-sm text-red-200">
          {error}
        </div>
      ) : null}
    </section>
  );
}

function renderBlock(block: Block) {
  switch (block.kind) {
    case "text":
      return <ModelRenderer key={block.id} block={block} />;
    case "tool":
      return <ToolRenderer key={block.id} block={block} />;
  }
}

function ThinkingIndicator() {
  return (
    <p className="m-0 flex items-center gap-1 text-sm text-slate-400">
      <span className="thinking-shimmer">Pensando</span>
      <span className="dots" aria-hidden />
    </p>
  );
}
