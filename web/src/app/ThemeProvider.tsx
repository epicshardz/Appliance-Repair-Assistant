"use client";

import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { applyTheme, lightTheme, darkTheme, ThemeColors } from "./theme";

type Theme = "light" | "dark" | "system";

interface ThemeContextType {
  theme: Theme;
  setTheme: (theme: Theme) => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<Theme>("system");

  useEffect(() => {
    // Initialize theme from localStorage or system preference
    const stored = localStorage.getItem("theme") as Theme;
    if (stored) {
      setTheme(stored);
    }
  }, []);

  useEffect(() => {
    const root = document.documentElement;
    root.removeAttribute("data-theme");

    if (theme === "system") {
      const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
      const applySystemTheme = (e: MediaQueryListEvent | MediaQueryList) => {
        root.setAttribute("data-theme", e.matches ? "dark" : "light");
        applyTheme(e.matches ? darkTheme : lightTheme);
      };

      mediaQuery.addEventListener("change", applySystemTheme);
      applySystemTheme(mediaQuery);

      return () => mediaQuery.removeEventListener("change", applySystemTheme);
    } else {
      root.setAttribute("data-theme", theme);
      applyTheme(theme === "dark" ? darkTheme : lightTheme);
    }

    // Store theme preference
    if (theme === "light" || theme === "dark") {
      localStorage.setItem("theme", theme);
    }
  }, [theme]);

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error("useTheme must be used within a ThemeProvider");
  }
  return context;
}

// Helper function for Android WebView
export function setWebViewTheme(isDark: boolean) {
  const theme = isDark ? "dark" : "light";
  const stored = localStorage.getItem("theme");
    if (!stored || !["light", "dark"].includes(stored)) {
    const root = document.documentElement;
    root.setAttribute("data-theme", theme);
    applyTheme(isDark ? darkTheme : lightTheme);
  }
}
