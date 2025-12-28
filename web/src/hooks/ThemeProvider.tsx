import { useCallback, type ReactNode } from "react";
import { ThemeContext, type Theme } from "./ThemeContext";
import { useLocalStorage } from "./useLocalStorage";

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useLocalStorage<Theme>("yubal-theme", "dark")

  const toggle = useCallback(() => {
    setTheme((prev) => (prev === "dark" ? "light" : "dark"));
  }, [setTheme]);

  const themeClass = theme === "dark" ? "flexoki-dark" : "flexoki-light";

  return (
    <ThemeContext.Provider value={{ theme, toggle }}>
      <main className={themeClass}>{children}</main>
    </ThemeContext.Provider>
  );
}
