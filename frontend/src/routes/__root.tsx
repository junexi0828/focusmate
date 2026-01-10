import { createRootRoute, Outlet, useLocation } from "@tanstack/react-router";
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

export const Route = createRootRoute({
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
            <header className="h-14 border-b border-border bg-card/50 backdrop-blur sticky top-0 z-10 flex items-center px-4">
              <div className="flex-1" />
              <div className="text-sm text-muted-foreground flex items-center gap-4">
                <NotificationBell />
                <kbd className="pointer-events-none inline-flex h-5 select-none items-center gap-1 rounded border bg-muted px-1.5 font-mono text-[10px] font-medium text-muted-foreground opacity-100">
                  <span className="text-xs">⌘</span>K
                </kbd>
                <span>FocusMate v2.0</span>
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
