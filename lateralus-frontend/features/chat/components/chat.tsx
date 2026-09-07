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
  const { messages, toolCall, isLoading, error, sendMessage, newChat } =
    useChat();
  const hasConversation = messages.length > 0 || Boolean(toolCall);

  return (
    <main className="relative flex min-h-screen overflow-hidden bg-[#04050d] text-slate-100">
      <BackgroundOrbs />

      <header className="fixed inset-x-0 top-0 z-20 flex h-[72px] items-center justify-between border-b border-blue-100/[0.08] bg-[#070a10]/70 px-5 backdrop-blur-xl">
        <div className="flex items-center gap-3">
          <span className="size-2.5 rounded-full bg-sky-300 shadow-[0_0_18px_rgba(125,211,252,0.9)]" />
          <span className="font-serif text-2xl tracking-wide text-slate-200">
            lateralus
          </span>
        </div>
        <NewChatButton onClick={newChat} />
      </header>

      <section className="relative z-10 flex min-h-screen w-full flex-col">
        {hasConversation ? (
          <MessageList
            messages={messages}
            toolCall={toolCall}
            isLoading={isLoading}
            error={error}
          />
        ) : (
          <EmptyState onPrompt={sendMessage} />
        )}

        <ChatInput disabled={isLoading} onSubmit={sendMessage} />
      </section>
    </main>
  );
}

function EmptyState({ onPrompt }: { onPrompt: (prompt: string) => void }) {
  return (
    <div className="mx-auto flex min-h-screen w-[min(92vw,980px)] flex-col items-center justify-center px-4 pb-28 text-center">
      <div className="mb-12 size-5 rounded-full bg-sky-300 shadow-[0_0_34px_rgba(125,211,252,0.85)]" />
      <h1 className="font-serif text-5xl text-slate-200 md:text-6xl">
        Por onde começamos?
      </h1>
      <p className="mt-5 text-lg text-slate-500">
        Pergunte o clima de uma cidade. O grafo streama a tool e o texto.
      </p>
      <div className="mt-9 flex flex-wrap justify-center gap-3">
        {prompts.map((prompt) => (
          <button
            key={prompt}
            type="button"
            onClick={() => onPrompt(prompt)}
            className="rounded-full bg-[#1b1c28] px-6 py-3 text-slate-300 shadow-[0_18px_50px_rgba(0,0,0,0.28)] transition hover:bg-[#222534] hover:text-slate-100"
          >
            {prompt}
          </button>
        ))}
      </div>
    </div>
  );
}

function BackgroundOrbs() {
  return (
    <>
      <div className="pointer-events-none absolute left-[12%] top-[10%] h-40 w-96 rounded-full bg-sky-500/10 blur-3xl" />
      <div className="pointer-events-none absolute bottom-0 right-0 h-72 w-72 rounded-full bg-blue-700/10 blur-3xl" />
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_50%_45%,rgba(147,197,253,0.04),transparent_28%),linear-gradient(180deg,rgba(219,234,254,0.03),transparent_14%)]" />
    </>
  );
}
