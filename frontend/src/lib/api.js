/**
 * @typedef {{ id: string, name: string, description: string, url: string, category: string, color: string, order: number, enabled: boolean }} PortalApp
 * @typedef {{ company: string, tagline: string }} PortalInfo
 * @typedef {Omit<PortalApp, 'id'> & { id: string }} AppCreate
 * @typedef {Partial<Omit<PortalApp, 'id'>>} AppUpdate
 */

const PUBLIC_API = '/api/public'
const PRIVATE_API = '/api/private'

/**
 * Send unauthenticated private-API callers through Discord OAuth (oauth2-proxy).
 * @param {Response} response
 */
function redirectToLoginIfNeeded(response) {
  if (response.status === 401 || response.status === 403) {
    const rd = encodeURIComponent(window.location.href)
    window.location.href = `/oauth2/sign_in?rd=${rd}`
  }
}

/**
 * @param {Response} response
 * @param {string} fallback
 */
async function readError(response, fallback) {
  try {
    const data = await response.json()
    if (typeof data?.detail === 'string') return data.detail
    if (Array.isArray(data?.detail)) {
      return data.detail.map((item) => item.msg ?? JSON.stringify(item)).join('; ')
    }
  } catch {
    // ignore parse errors
  }
  return fallback
}

/**
 * @returns {Promise<PortalInfo>}
 */
export async function fetchPortalInfo() {
  const response = await fetch(`${PUBLIC_API}/portal`)
  if (!response.ok) {
    throw new Error('Failed to load portal info')
  }
  return response.json()
}

/**
 * @param {{ includeDisabled?: boolean }} [options]
 * @returns {Promise<PortalApp[]>}
 */
export async function fetchApps(options = {}) {
  const base = options.includeDisabled ? PRIVATE_API : PUBLIC_API
  const response = await fetch(`${base}/apps`, { credentials: 'same-origin' })
  if (options.includeDisabled) redirectToLoginIfNeeded(response)
  if (!response.ok) {
    throw new Error(await readError(response, 'Failed to load applications'))
  }
  return response.json()
}

/**
 * @param {AppCreate} payload
 * @returns {Promise<PortalApp>}
 */
export async function createApp(payload) {
  const response = await fetch(`${PRIVATE_API}/apps`, {
    method: 'POST',
    credentials: 'same-origin',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  redirectToLoginIfNeeded(response)
  if (!response.ok) {
    throw new Error(await readError(response, 'Failed to create app'))
  }
  return response.json()
}

/**
 * @param {string} id
 * @param {AppUpdate} payload
 * @returns {Promise<PortalApp>}
 */
export async function updateApp(id, payload) {
  const response = await fetch(`${PRIVATE_API}/apps/${encodeURIComponent(id)}`, {
    method: 'PUT',
    credentials: 'same-origin',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  redirectToLoginIfNeeded(response)
  if (!response.ok) {
    throw new Error(await readError(response, 'Failed to update app'))
  }
  return response.json()
}

/**
 * @param {string} id
 * @returns {Promise<void>}
 */
export async function deleteApp(id) {
  const response = await fetch(`${PRIVATE_API}/apps/${encodeURIComponent(id)}`, {
    method: 'DELETE',
    credentials: 'same-origin',
  })
  redirectToLoginIfNeeded(response)
  if (!response.ok) {
    throw new Error(await readError(response, 'Failed to delete app'))
  }
}
