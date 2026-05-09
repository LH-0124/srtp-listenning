(function () {
  const root = document.documentElement;
  const toggle = document.getElementById("themeToggle");
  const label = document.getElementById("themeLabel");
  const icon = toggle ? toggle.querySelector(".theme-icon") : null;
  const storageKey = "capd-demo-theme";

  function applyTheme(theme) {
    root.dataset.theme = theme;
    const isDark = theme === "dark";
    if (toggle) {
      toggle.setAttribute("aria-pressed", String(isDark));
    }
    if (label) {
      label.textContent = isDark ? "Light mode" : "Dark mode";
    }
    if (icon) {
      icon.textContent = isDark ? "Sun" : "Moon";
    }
  }

  const savedTheme = localStorage.getItem(storageKey);
  const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  applyTheme(savedTheme || (prefersDark ? "dark" : "light"));

  if (toggle) {
    toggle.addEventListener("click", function () {
      const nextTheme = root.dataset.theme === "dark" ? "light" : "dark";
      localStorage.setItem(storageKey, nextTheme);
      applyTheme(nextTheme);
    });
  }
})();
