import type { ToolCallState } from "../types";

type ToolRendererProps = {
  toolCall: ToolCallState;
};

export function ToolRenderer({ toolCall }: ToolRendererProps) {
  const payload = toolCall.payload;
  const city = payload?.city ?? toolCall.city ?? "cidade";
  const condition = payload?.condition ?? "Consultando o clima";
  const temp = typeof payload?.temp_c === "number" ? payload.temp_c : undefined;
  const isComplete = toolCall.status === "complete";

  return (
    <div className="relative ml-8 w-[min(100%,760px)]">
      <span className="absolute -left-8 top-6 size-2.5 rounded-full bg-sky-300 shadow-[0_0_18px_rgba(125,211,252,0.9)]" />
      <article className="rounded-[1.35rem] border border-sky-100/20 bg-[#0f172a]/90 p-6 shadow-[0_24px_70px_rgba(0,0,0,0.35),0_0_42px_rgba(56,189,248,0.08)] backdrop-blur-xl">
        <div className="flex items-center gap-3">
          <StatusIcon complete={isComplete} />
          <span className="font-mono text-lg font-semibold text-slate-200">
            {toolCall.name}
          </span>
          <span className="rounded-full bg-black/25 px-3 py-1 text-xs text-slate-400">
            {city}
          </span>
          {toolCall.durationSeconds ? (
            <span className="ml-auto text-xs text-slate-500">
              {toolCall.durationSeconds.toFixed(1)}s
            </span>
          ) : null}
        </div>

        <div className="mt-5 h-0.5 w-full overflow-hidden rounded-full bg-sky-100/15">
          <div
            className={`h-full rounded-full bg-sky-300 shadow-[0_0_18px_rgba(56,189,248,0.45)] ${
              isComplete
                ? "w-full"
                : "animate-[loading-progress_2.2s_ease-out_forwards]"
            }`}
          />
        </div>

        {!isComplete ? (
          <div>
            <p className="mt-5 text-xl text-slate-400">
              Consultando o clima em {city}...
            </p>
          </div>
        ) : (
          <>
            <div className="mt-6 flex items-center gap-7 rounded-xl bg-[#080f1f] px-8 py-6">
              <WeatherIcon />
              <div className="flex items-start gap-2">
                <span className="text-5xl leading-none text-slate-100">
                  {temp ?? "--"}
                </span>
                <span className="pt-1 text-2xl text-slate-200">°C</span>
              </div>
              <div>
                <p className="text-xl text-slate-300">{capitalize(condition)}</p>
                <p className="mt-2 text-sm uppercase tracking-[0.35em] text-slate-500">
                  {city}
                </p>
              </div>
            </div>

            <details open className="mt-5">
              <summary className="cursor-pointer select-none font-mono text-xs uppercase tracking-[0.28em] text-slate-500">
                JSON
              </summary>
              <pre className="mt-3 overflow-auto rounded-xl bg-black/45 p-4 font-mono text-sm leading-7 text-slate-300">
                {JSON.stringify(toolCall.rawJson ?? payload, null, 2)}
              </pre>
            </details>
          </>
        )}
      </article>
    </div>
  );
}

function StatusIcon({ complete }: { complete: boolean }) {
  return (
    <span
      className={`grid size-5 place-items-center rounded-full border ${
        complete
          ? "border-emerald-300/70 text-emerald-200"
          : "animate-spin border-slate-500 border-t-sky-300"
      }`}
    >
      {complete ? <span className="text-xs">✓</span> : null}
    </span>
  );
}

function WeatherIcon() {
  return (
    // eslint-disable-next-line @next/next/no-img-element
    <img
      aria-hidden
      src="/partly-cloudy.png"
      alt=""
      className="size-20 object-contain brightness-0 invert drop-shadow-[0_0_16px_rgba(191,219,254,0.35)]"
    />
  );
}

function capitalize(value: string) {
  return value.charAt(0).toUpperCase() + value.slice(1);
}
