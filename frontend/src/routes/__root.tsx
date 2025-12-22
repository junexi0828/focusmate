import { createRootRoute, Outlet, useLocation } from "@tanstack/react-router";
import { useEffect } from "react";
import { TanStackRouterDevtools } from "@tanstack/react-router-devtools";
import { Toaster } from "sonner";
import { Sidebar } from "../components/Sidebar";
import { ErrorBoundary } from "../components/ErrorBoundary";
import { CommandPalette } from "../components/CommandPalette";
import { NotificationBell } from "../components/notifications/NotificationBell";
import { Footer } from "../components/footer";
import { InteractiveCursor } from "../components/InteractiveCursor";

export const Route = createRootRoute({
  component: RootComponent,
});

function RootComponent() {
  const location = useLocation();

  // Unified theme initialization
  useEffect(() => {
    const applyTheme = () => {
      const savedTheme = localStorage.getItem("theme");
      const root = document.documentElement;
      root.classList.remove("light", "dark");

      if (savedTheme === "dark") {
        root.classList.add("dark");
      } else if (savedTheme === "light") {
        root.classList.add("light");
      } else {
        // Fallback to system preference if no specific theme is saved
        const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
        root.classList.add(prefersDark ? "dark" : "light");
      }
    };

    applyTheme();

    // Optional: Listen for system theme changes if no explicit theme is set
    const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
    const handler = () => {
      if (!localStorage.getItem("theme")) {
        applyTheme();
      }
    };

    mediaQuery.addEventListener("change", handler);
    return () => mediaQuery.removeEventListener("change", handler);
  }, []);

  // Hide sidebar on login page
  const isLoginPage = location.pathname === "/login";

  return (
    <ErrorBoundary>
      <div className="flex h-screen bg-background text-foreground font-sans antialiased selection:bg-primary/20">
        {/* Persistent Sidebar - Hidden on Login */}
        {!isLoginPage && <Sidebar />}

        {/* Main Content Area */}
        <main className="flex-1 overflow-auto relative flex flex-col">
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
              isLoginPage
                ? "h-full w-full"
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

        {/* Interactive Cursor Effect */}
        <InteractiveCursor />

        {/* Global Toaster for Notifications */}
        <Toaster position="top-center" richColors />

        {/* DevTools (only in dev) */}
        <TanStackRouterDevtools />
      </div>
    </ErrorBoundary>
  );
}
