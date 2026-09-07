type NewChatButtonProps = {
  onClick: () => void;
};

export function NewChatButton({ onClick }: NewChatButtonProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="rounded-full border border-sky-100/10 bg-sky-100/[0.03] px-4 py-2 text-sm text-slate-300 shadow-[0_0_24px_rgba(56,189,248,0.06)] transition hover:border-sky-200/30 hover:bg-sky-100/10 hover:text-slate-100"
    >
      Novo chat
    </button>
  );
}
