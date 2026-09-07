import type { TextBlock } from "../blocks";

type ModelRendererProps = {
  block: TextBlock;
};

export function ModelRenderer({ block }: ModelRendererProps) {
  if (!block.text.trim()) return null;

  return (
    <div className="w-[min(100%,720px)] whitespace-pre-wrap text-base leading-8 text-slate-200">
      {block.text}
      {block.streaming ? (
        <span
          className="ml-1 inline-block h-5 w-0.5 translate-y-1 bg-cyan-300"
          aria-hidden
        />
      ) : null}
    </div>
  );
}
