import { useCallback, useEffect, type ReactNode } from "react";
import { ThemeContext, type Theme } from "./ThemeContext";
import { useLocalStorage } from "./useLocalStorage";

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useLocalStorage<Theme>("yubal-theme", "dark");

  const toggle = useCallback(() => {
    setTheme((prev) => (prev === "dark" ? "light" : "dark"));
  }, [setTheme]);

  const themeClass = theme === "dark" ? "flexoki-dark" : "flexoki-light";

  // Sync theme class to document.documentElement for View Transitions API
  useEffect(() => {
    const root = document.documentElement;
    root.classList.remove("flexoki-dark", "flexoki-light");
    root.classList.add(themeClass);
  }, [themeClass]);

  return (
    <ThemeContext.Provider value={{ theme, toggle }}>
      <main className={themeClass}>{children}</main>
    </ThemeContext.Provider>
  );
}
