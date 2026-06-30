import { NextRequest } from "next/server";

export function GET() {
  return new Response(undefined, { status: 404 });
}

export function POST(request: NextRequest) {
  const url = new URL(request.url);
  url.pathname = `${url.pathname}/`;
  return Response.redirect(url, 307);
}
