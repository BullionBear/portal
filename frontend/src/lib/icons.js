/** Simple inline SVG marks keyed by app.icon from the API. */
export const ICONS = {
  grafana: `<path d="M12 3.5 4.5 17.5h15L12 3.5Z" fill="currentColor"/><circle cx="12" cy="15.5" r="1.6" fill="#fff"/>`,
  jira: `<path d="M12.2 3.5c-.4 1.8-1.8 3.2-3.6 3.6 1.8.4 3.2 1.8 3.6 3.6.4-1.8 1.8-3.2 3.6-3.6-1.8-.4-3.2-1.8-3.6-3.6Z" fill="currentColor"/><path d="M8.2 9.4c-.5 2.2-2.2 3.9-4.4 4.4 2.2.5 3.9 2.2 4.4 4.4.5-2.2 2.2-3.9 4.4-4.4-2.2-.5-3.9-2.2-4.4-4.4Z" fill="currentColor" opacity=".75"/>`,
  gitlab: `<path d="M12 20.5 4.8 8.8l1.7-4.3L9 11h6l2.5-6.5 1.7 4.3L12 20.5Z" fill="currentColor"/>`,
  confluence: `<path d="M7 7.5c2.4 1.6 4.2 4.4 5 7.2.8-2.8 2.6-5.6 5-7.2-2.8 1-5.2 3.2-6.4 6.1C9.4 10.7 8 8.5 7 7.5Z" fill="currentColor"/><path d="M17 16.5c-2.4-1.6-4.2-4.4-5-7.2-.8 2.8-2.6 5.6-5 7.2 2.8-1 5.2-3.2 6.4-6.1 1.2 2.9 2.6 5.1 3.6 6.1Z" fill="currentColor" opacity=".7"/>`,
  prometheus: `<circle cx="12" cy="12" r="7.5" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M12 6.5v5.2l3.2 2" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>`,
  custom: `<rect x="5" y="5" width="14" height="14" rx="3" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M9 12h6M12 9v6" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>`,
  default: `<circle cx="12" cy="12" r="7" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M9 12h6" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>`,
}

/**
 * @param {string} key
 * @returns {string}
 */
export function iconMarkup(key) {
  return ICONS[key] ?? ICONS.default
}
