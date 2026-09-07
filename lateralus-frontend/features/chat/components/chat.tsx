"use client";

import { ChatInput } from "./chat-input";
import { MessageList } from "./message-list";
import { NewChatButton } from "./new-chat-button";
import { useChat } from "../use-chat";

const prompts = [
  "Qual o clima em São Paulo?",
  "Como está o tempo no Rio de Janeiro?",
  "Vai chover em Curitiba hoje?",
];

export function Chat() {
  const { turns, isLoading, error, sendMessage, newChat } = useChat();
  const hasConversation = turns.length > 0;

  return (
    <main className="flex min-h-screen flex-col bg-[#07090f] text-slate-100">
      <header className="sticky top-0 z-20 flex h-16 items-center justify-between border-b border-white/10 bg-[#0b0f16]/90 px-5 backdrop-blur">
        <div className="flex items-center gap-3">
          <span className="size-2.5 rounded-full bg-cyan-300 shadow-[0_0_16px_rgba(103,232,249,0.65)]" />
          <span className="font-serif text-2xl tracking-wide text-slate-100">
            lateralus
          </span>
        </div>
        <NewChatButton onClick={newChat} />
      </header>

      {hasConversation ? (
        <MessageList turns={turns} isLoading={isLoading} error={error} />
      ) : (
        <EmptyState onPrompt={sendMessage} />
      )}

      <ChatInput disabled={isLoading} onSubmit={sendMessage} />
    </main>
  );
}

function EmptyState({ onPrompt }: { onPrompt: (prompt: string) => void }) {
  return (
    <section className="mx-auto flex min-h-[calc(100vh-4rem)] w-[min(92vw,760px)] flex-1 flex-col justify-center px-4 pb-32 text-center">
      <span className="mx-auto mb-8 size-4 rounded-full bg-cyan-300 shadow-[0_0_30px_rgba(103,232,249,0.7)]" />
      <h1 className="font-serif text-5xl text-slate-100 md:text-6xl">
        Por onde começamos?
      </h1>
      <p className="mx-auto mt-5 max-w-xl text-base leading-7 text-slate-400">
        Pergunte o clima de uma cidade. A resposta mostra o evento da tool e,
        depois, o texto final do modelo.
      </p>
      <div className="mt-9 flex flex-wrap justify-center gap-3">
        {prompts.map((prompt) => (
          <button
            key={prompt}
            type="button"
            onClick={() => onPrompt(prompt)}
            className="rounded-full border border-white/10 bg-[#111827] px-5 py-3 text-sm text-slate-300 transition hover:border-cyan-200/40 hover:bg-[#172033] hover:text-slate-100"
          >
            {prompt}
          </button>
        ))}
      </div>
    </section>
  );
}
