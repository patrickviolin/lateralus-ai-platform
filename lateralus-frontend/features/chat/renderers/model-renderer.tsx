type ModelRendererProps = {
  content: string;
};

export function ModelRenderer({ content }: ModelRendererProps) {
  if (!content.trim()) {
    return null;
  }

  return (
    <div className="ml-8 w-[min(100%,760px)] text-lg leading-8 text-slate-200">
      {content}
    </div>
  );
}
