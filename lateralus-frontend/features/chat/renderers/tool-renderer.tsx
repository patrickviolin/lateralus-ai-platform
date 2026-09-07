import { toolCity, type ToolBlock } from "../blocks";
import { formatJson } from "../stream";

type ToolRendererProps = {
  block: ToolBlock;
};

export function ToolRenderer({ block }: ToolRendererProps) {
  const isDone = block.status === "done";
  const payload = block.payload;
  const city = toolCity(block);
  const condition = payload?.condition ?? "Consultando o clima";
  const temp = typeof payload?.temp_c === "number" ? payload.temp_c : undefined;
  const elapsed = elapsedLabel(block);

  return (
    <article
      className="w-[min(100%,520px)] rounded-lg border border-white/10 bg-[#0f172a] p-4 shadow-[0_18px_42px_rgba(0,0,0,0.28)]"
      aria-live="polite"
      aria-busy={!isDone}
    >
      <header className="flex min-h-6 items-center gap-3">
        <StatusIcon complete={isDone} />
        <code className="font-mono text-sm text-slate-100">{block.name}</code>
        <span className="max-w-48 truncate rounded-full border border-white/10 bg-black/20 px-2.5 py-1 text-xs text-slate-400">
          {city}
        </span>
        {elapsed ? (
          <span className="ml-auto font-mono text-xs text-slate-500">
            {elapsed}
          </span>
        ) : null}
      </header>

      <div className="mt-3 h-0.5 overflow-hidden rounded-full bg-white/10">
        <span
          className={`block h-full rounded-full bg-cyan-300 ${
            isDone ? "w-full" : "animate-[loading-progress_2.2s_ease-out_forwards]"
          }`}
        />
      </div>

      {isDone ? (
        <div className="mt-4">
          <div className="grid grid-cols-[64px_minmax(0,1fr)] gap-4 rounded-md border border-white/10 bg-[#070b13] p-4">
            <WeatherIcon />
            <div>
              <div className="flex items-start gap-2">
                <span className="text-4xl leading-none text-slate-100">
                  {temp ?? "--"}
                </span>
                <span className="pt-1 text-lg text-slate-300">°C</span>
              </div>
              <p className="mt-2 text-sm text-slate-300">
                {capitalize(condition)}
              </p>
              <p className="mt-1 text-xs uppercase text-slate-500">{city}</p>
            </div>
          </div>

          <details className="mt-3">
            <summary className="cursor-pointer select-none font-mono text-xs uppercase text-slate-500">
              JSON
            </summary>
            <pre className="mt-2 max-h-56 overflow-auto rounded-md bg-black/35 p-3 font-mono text-xs leading-6 text-slate-300">
              {formatJson(block.output)}
            </pre>
          </details>
        </div>
      ) : (
        <p className="m-0 mt-3 text-sm text-slate-400">
          Consultando o clima em {city}
          <span className="dots" aria-hidden />
        </p>
      )}
    </article>
  );
}

function StatusIcon({ complete }: { complete: boolean }) {
  return (
    <span
      className={`grid size-5 place-items-center rounded-full border ${
        complete
          ? "border-emerald-300/70 text-emerald-200"
          : "animate-spin border-slate-500 border-t-cyan-300"
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
      className="size-16 object-contain brightness-0 invert drop-shadow-[0_0_16px_rgba(191,219,254,0.3)]"
    />
  );
}

function elapsedLabel(block: ToolBlock): string | undefined {
  if (block.startedAt === undefined || block.endedAt === undefined) return undefined;
  return `${((block.endedAt - block.startedAt) / 1000).toFixed(1)}s`;
}

function capitalize(value: string) {
  return value.charAt(0).toUpperCase() + value.slice(1);
}
