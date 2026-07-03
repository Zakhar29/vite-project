export const THEME_STORAGE_KEY = "melo_theme";

export const THEMES = {
  standard: {
    id: "standard",
    label: "Стандартная",
  },
  dark: {
    id: "dark",
    label: "Тёмная",
  },
  light: {
    id: "light",
    label: "Светлая",
  },
};

export const THEME_OPTIONS = Object.values(THEMES);

export function getThemeLabel(themeId) {
  return THEMES[themeId]?.label || THEMES.standard.label;
}

export function getThemeIdByLabel(label) {
  const match = THEME_OPTIONS.find((theme) => theme.label === label);
  return match?.id || THEMES.standard.id;
}

export function getStoredTheme() {
  const stored = localStorage.getItem(THEME_STORAGE_KEY);
  if (stored && THEMES[stored]) {
    return stored;
  }
  return THEMES.standard.id;
}

export function applyTheme(themeId) {
  const resolved = THEMES[themeId] ? themeId : THEMES.standard.id;
  document.documentElement.setAttribute("data-theme", resolved);
  return resolved;
}

export function setTheme(themeId) {
  const resolved = applyTheme(themeId);
  localStorage.setItem(THEME_STORAGE_KEY, resolved);
  window.dispatchEvent(new CustomEvent("themechange", { detail: { theme: resolved } }));
  return resolved;
}

export function initTheme() {
  return applyTheme(getStoredTheme());
}
