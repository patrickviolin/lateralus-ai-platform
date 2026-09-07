const BACKEND_API_BASE_URL =
  process.env.BACKEND_API_BASE_URL ?? "http://localhost:8000";

export async function POST(request: Request) {
  const response = await fetch(`${BACKEND_API_BASE_URL}/agent/execute`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "text/event-stream",
    },
    body: await request.text(),
  });

  if (!response.ok || !response.body) {
    return Response.json(
      { message: `Backend request failed with status ${response.status}` },
      { status: response.status || 502 },
    );
  }

  return new Response(response.body, {
    status: response.status,
    headers: {
      "Content-Type": "text/event-stream; charset=utf-8",
      "Cache-Control": "no-cache, no-transform",
      Connection: "keep-alive",
    },
  });
}
