import { SESSION_COOKIES } from '@/lib/session';
import { NextResponse } from 'next/server';

export function GET(request: Request) {
  const response = NextResponse.redirect(new URL('/login', request.url));
  for (const name of SESSION_COOKIES) {
    response.cookies.set(name, '', { path: '/', maxAge: 0 });
  }
  return response;
}
