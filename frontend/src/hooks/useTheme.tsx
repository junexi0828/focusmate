/**
 * Theme provider hook for dark mode toggle
 */

import { createContext, useContext, useEffect, useState } from "react";

type Theme = "dark" | "light" | "system";

type ThemeProviderProps = {
  children: React.ReactNode;
  defaultTheme?: Theme;
  storageKey?: string;
};

type ThemeProviderState = {
  theme: Theme;
  setTheme: (theme: Theme) => void;
  isFunMode: boolean;
  toggleFunMode: () => void;
};

const initialState: ThemeProviderState = {
  theme: "system",
  setTheme: () => null,
  isFunMode: false,
  toggleFunMode: () => null,
};

const ThemeProviderContext = createContext<ThemeProviderState>(initialState);

export function ThemeProvider({
  children,
  defaultTheme = "system",
  storageKey = "focusmate-ui-theme",
  ...props
}: ThemeProviderProps) {
  const [theme, setThemeState] = useState<Theme>(
    () => (localStorage.getItem(storageKey) as Theme) || defaultTheme
  );

  const [isFunMode, setIsFunMode] = useState<boolean>(
    () => localStorage.getItem("focusmate-ui-fun-mode") === "true"
  );

  useEffect(() => {
    const root = window.document.documentElement;

    // Reset all potential classes
    root.classList.remove("light", "dark", "fun");

    // Apply base theme
    if (theme === "system") {
      const systemTheme = window.matchMedia("(prefers-color-scheme: dark)")
        .matches
        ? "dark"
        : "light";
      root.classList.add(systemTheme);
    } else {
      root.classList.add(theme);
    }

    // Apply Fun mode (3D effects) regardless of base theme
    if (isFunMode) {
      root.classList.add("fun");
    }
  }, [theme, isFunMode]);

  const value = {
    theme,
    setTheme: (newTheme: Theme) => {
      localStorage.setItem(storageKey, newTheme);
      setThemeState(newTheme);
    },
    isFunMode,
    toggleFunMode: () => {
      const newValue = !isFunMode;
      localStorage.setItem("focusmate-ui-fun-mode", String(newValue));
      setIsFunMode(newValue);
    }
  };

  return (
    <ThemeProviderContext.Provider {...props} value={value}>
      {children}
    </ThemeProviderContext.Provider>
  );
}

export const useTheme = () => {
  const context = useContext(ThemeProviderContext);

  if (context === undefined)
    throw new Error("useTheme must be used within a ThemeProvider");

  return context;
};
