import { useCallback, useEffect, useState, type ReactNode } from "react";
import { ThemeContext, STORAGE_KEY, type Theme } from "./ThemeContext";

function getStoredTheme(): Theme {
  if (typeof window === "undefined") return "dark";
  const stored = localStorage.getItem(STORAGE_KEY);
  return stored === "light" ? "light" : "dark";
}

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<Theme>(getStoredTheme);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, theme);
  }, [theme]);

  const toggle = useCallback(() => {
    setTheme((prev) => (prev === "dark" ? "light" : "dark"));
  }, []);

  const themeClass = theme === "dark" ? "flexoki-dark" : "flexoki-light";

  return (
    <ThemeContext.Provider value={{ theme, toggle }}>
      <main className={themeClass}>{children}</main>
    </ThemeContext.Provider>
  );
}
