import {
  createRootRoute,
  Outlet,
  redirect,
  useLocation,
} from "@tanstack/react-router";
import { lazy, Suspense } from "react";
import { Toaster } from "sonner";

// Conditionally import TanStackRouterDevtools only in development
const TanStackRouterDevtools = import.meta.env.DEV
  ? lazy(() =>
      import("@tanstack/react-router-devtools").then((d) => ({
        default: d.TanStackRouterDevtools,
      }))
    )
  : null;
import { Sidebar } from "../components/Sidebar";
import { ErrorBoundary } from "../components/ErrorBoundary";
import { CommandPalette } from "../components/CommandPalette";
import { NotificationBell } from "../components/notifications/NotificationBell";
import { Footer } from "../components/footer";

import { useTheme } from "../hooks/useTheme";
// ThemeToggle removed as unused
import { BackgroundBlobs } from "../components/ui/BackgroundBlobs";
import { ScrollingTicker } from "../components/layout/GlobalTicker";
import { Sparkles } from "lucide-react";
import { authService } from "../features/auth/services/authService";

export const Route = createRootRoute({
  beforeLoad: ({ location }) => {
    const pathname = location.pathname || "/";
    const isPublicPath =
      pathname === "/" ||
      pathname === "/login" ||
      pathname.startsWith("/auth/");

    if (isPublicPath) {
      return;
    }

    const isAuthenticated =
      authService.isAuthenticated() && !authService.isTokenExpired();

    if (!isAuthenticated) {
      throw redirect({ to: "/login" });
    }
  },
  component: RootComponent,
});

function RootComponent() {
  const location = useLocation();
  const { isFunMode } = useTheme();

  // Hide sidebar on login page
  const isLoginPage = location.pathname === "/login";
  const isHomePage = location.pathname === "/";

  return (
    <ErrorBoundary>
      <div className="flex h-screen bg-background text-foreground font-sans antialiased selection:bg-primary/20">
        {isFunMode && <BackgroundBlobs />}
        {/* Persistent Sidebar - Hidden on Login */}
        {!isLoginPage && <Sidebar />}

        {/* Global Theme Toggle (Upper Right) - Removed as Sidebar handles it */}
        {/* {!isLoginPage && <ThemeToggle className="fixed top-4 right-4 z-50" />} */}

        {/* Main Content Area */}
            <main
          className={`flex-1 overflow-auto relative flex flex-col ${
            isHomePage && isFunMode ? "mesh-gradient" : ""
          }`}
        >
          {/* Top Header Placeholder (optional) - Hidden on Login */}
          {!isLoginPage && (
            <header className="h-14 border-b border-border bg-card/50 backdrop-blur sticky top-0 z-10 flex items-center px-4 relative">
              {/* Left Spacer / Breadcrumbs area */}
              <div className="flex-1" />

              {/* Center: Global Ticker (Megaphone) */}
              <div className="absolute left-1/2 top-1/2 -translate-y-1/2 -translate-x-1/2 hidden md:block">
                <ScrollingTicker />
              </div>

              {/* Right: Actions */}
              <div className="text-sm text-muted-foreground flex items-center gap-3">
                <NotificationBell />
                <kbd className="pointer-events-none hidden md:inline-flex h-5 select-none items-center gap-1 rounded border bg-muted px-1.5 font-mono text-[10px] font-medium text-muted-foreground opacity-100">
                  <span className="text-xs">⌘</span>K
                </kbd>

                {/* AI Chatbot Trigger */}
                 <div className="w-px h-4 bg-border mx-1" />
                 <button className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-primary/10 text-primary hover:bg-primary/20 transition-all duration-300 hover:scale-105 group">
                    <Sparkles className="w-3.5 h-3.5 transition-transform group-hover:rotate-12" />
                    <span className="text-xs font-bold">AI Chat</span>
                </button>
              </div>
            </header>
          )}

          <div
            className={
              isLoginPage || isHomePage
                ? "flex-1 w-full"
                : "flex-1 p-8 max-w-7xl mx-auto w-full"
            }
          >
            <Outlet />
          </div>

          {/* Footer - Hidden on Login */}
          {!isLoginPage && <Footer />}
        </main>

        {/* Command Palette (⌘K) */}
        {!isLoginPage && <CommandPalette />}

        {/* Global Toaster for Notifications */}
        <Toaster position="top-center" richColors />

        {/* DevTools (only in dev) */}
        {TanStackRouterDevtools && (
          <Suspense fallback={null}>
            <TanStackRouterDevtools />
          </Suspense>
        )}
      </div>
    </ErrorBoundary>
  );
}
