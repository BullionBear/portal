/**
 * Tiny pathname router (no dependency).
 * @param {string} path
 */
export function navigate(path) {
  if (path === window.location.pathname) return
  window.history.pushState({}, '', path)
  window.dispatchEvent(new PopStateEvent('popstate'))
}

/**
 * @returns {string}
 */
export function currentPath() {
  return window.location.pathname.replace(/\/+$/, '') || '/'
}

/**
 * @param {MouseEvent} event
 * @param {string} path
 */
export function handleLinkClick(event, path) {
  if (
    event.defaultPrevented ||
    event.button !== 0 ||
    event.metaKey ||
    event.ctrlKey ||
    event.shiftKey ||
    event.altKey
  ) {
    return
  }
  event.preventDefault()
  navigate(path)
}
