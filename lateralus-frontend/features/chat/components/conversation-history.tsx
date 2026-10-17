import type { Conversation } from "../types";

type ConversationHistoryProps = {
  conversations: Conversation[];
  activeConversationId: string | null;
  onSelect: (id: string) => void;
  onNewChat: () => void;
  onClose: () => void;
  open: boolean;
};

export function ConversationHistory({
  conversations,
  activeConversationId,
  onSelect,
  onNewChat,
  onClose,
  open,
}: ConversationHistoryProps) {
  return (
    <>
      {open ? (
        <button
          type="button"
          aria-label="Fechar histórico"
          onClick={onClose}
          className="fixed inset-0 z-30 bg-black/70 md:hidden"
        />
      ) : null}
      <aside
        aria-label="Histórico de conversas"
        className={`${open ? "flex" : "hidden"} fixed inset-y-0 left-0 z-40 w-[min(85vw,288px)] flex-col border-r border-white/10 bg-[#0b0f16] md:sticky md:top-0 md:flex md:h-screen md:w-72 md:shrink-0`}
      >
        <div className="flex h-16 items-center justify-between border-b border-white/10 px-4">
          <h2 className="text-sm font-semibold text-slate-200">Conversas</h2>
          <button
            type="button"
            onClick={onClose}
            aria-label="Fechar histórico"
            className="rounded-md px-2 py-1 text-slate-400 hover:bg-white/10 hover:text-white md:hidden"
          >
            ✕
          </button>
        </div>
        <div className="px-3 pt-4">
          <button
            type="button"
            onClick={() => { onNewChat(); onClose(); }}
            className="w-full rounded-xl border border-sky-100/15 px-4 py-3 text-left text-sm text-slate-200 transition hover:border-cyan-300/40 hover:bg-white/5"
          >
            + Novo chat
          </button>
        </div>
        <nav aria-label="Conversas anteriores" className="min-h-0 flex-1 overflow-y-auto px-3 py-5">
          {conversations.length === 0 ? (
            <p className="px-2 text-sm leading-6 text-slate-500">
              Suas conversas aparecerão aqui enquanto esta página estiver aberta.
            </p>
          ) : (
            <ul className="space-y-1">
              {conversations.map((chat) => (
                <li key={chat.id}>
                  <button
                    type="button"
                    onClick={() => { onSelect(chat.id); onClose(); }}
                    aria-current={chat.id === activeConversationId ? "page" : undefined}
                    title={chat.title}
                    className={`w-full truncate rounded-xl px-3 py-3 text-left text-sm transition ${
                      chat.id === activeConversationId
                        ? "bg-cyan-300/10 text-cyan-100"
                        : "text-slate-400 hover:bg-white/5 hover:text-slate-100"
                    }`}
                  >
                    {chat.title}
                  </button>
                </li>
              ))}
            </ul>
          )}
        </nav>
      </aside>
    </>
  );
}
