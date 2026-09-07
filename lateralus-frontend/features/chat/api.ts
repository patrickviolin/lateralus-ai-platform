export async function executeAgent(message: string, signal?: AbortSignal) {
  const response = await fetch("/api/agent/execute", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "text/event-stream",
    },
    body: JSON.stringify({ message }),
    signal,
  });

  if (!response.ok) {
    throw new Error(`Agent request failed with status ${response.status}`);
  }

  if (!response.body) {
    throw new Error("Agent response did not include a stream body");
  }

  return response.body;
}
