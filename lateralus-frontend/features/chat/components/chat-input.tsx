"use client";

import { FormEvent, KeyboardEvent, useState } from "react";

type ChatInputProps = {
  disabled?: boolean;
  onSubmit: (message: string) => void;
};

export function ChatInput({ disabled, onSubmit }: ChatInputProps) {
  const [message, setMessage] = useState("");

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!message.trim() || disabled) {
      return;
    }

    onSubmit(message);
    setMessage("");
  }

  function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      event.currentTarget.form?.requestSubmit();
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="fixed inset-x-0 bottom-5 z-20 mx-auto w-[min(92vw,960px)] px-4"
    >
      <div className="group flex min-h-16 items-center gap-3 rounded-[2rem] border border-sky-100/20 bg-[#151521]/90 px-6 py-3 shadow-[0_0_40px_rgba(56,189,248,0.13)] backdrop-blur-xl transition focus-within:border-sky-200/50 focus-within:shadow-[0_0_55px_rgba(56,189,248,0.22)]">
        <textarea
          value={message}
          onChange={(event) => setMessage(event.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          placeholder="Pergunte alguma coisa"
          rows={1}
          className="max-h-32 min-h-8 min-w-0 flex-1 resize-none bg-transparent text-lg text-slate-100 outline-none placeholder:text-slate-500 disabled:cursor-not-allowed"
        />
        <button
          type="submit"
          disabled={disabled || !message.trim()}
          aria-label="Enviar mensagem"
          className="grid size-12 place-items-center rounded-full bg-blue-200 text-[#030408] shadow-[0_0_28px_rgba(56,189,248,0.28)] transition hover:bg-blue-300 disabled:cursor-not-allowed disabled:opacity-50"
        >
          <span aria-hidden>↑</span>
        </button>
      </div>
      <p className="mt-2 text-center text-xs text-slate-600">
        Enter envia · Shift+Enter quebra linha
      </p>
    </form>
  );
}
