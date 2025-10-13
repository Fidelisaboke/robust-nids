import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Get token from cookie or check if it exists (we're using sessionStorage in client)
  // Since we're using sessionStorage, middleware will redirect to login for protected routes
  // The actual auth check happens on the client side

  // Public routes that don't require authentication
  const publicRoutes = ['/', '/login', '/reset-password', '/verify-email'];
  const isPublicRoute = publicRoutes.some((route) => pathname === route || pathname.startsWith('/login'));

  // Auth routes that should redirect to dashboard if already authenticated
  const authRoutes = ['/login', '/reset-password', '/verify-email'];
  const isAuthRoute = authRoutes.some((route) => pathname.startsWith(route));

  // Protected routes
  const protectedRoutes = ['/dashboard', '/admin', '/settings', '/alerts', '/metrics', '/reports'];
  const isProtectedRoute = protectedRoutes.some((route) => pathname.startsWith(route));

  // Allow all routes to pass through
  // Authentication will be handled on the client side via AuthContext
  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public files
     */
    '/((?!api|_next/static|_next/image|favicon.ico|.*\\.svg|.*\\.png).*)',
  ],
};
