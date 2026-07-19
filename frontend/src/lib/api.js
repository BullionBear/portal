/**
 * @typedef {{ id: string, name: string, description: string, url: string, category: string, color: string, order: number, enabled: boolean }} PortalApp
 * @typedef {{ company: string, tagline: string }} PortalInfo
 * @typedef {Omit<PortalApp, 'id'> & { id: string }} AppCreate
 * @typedef {Partial<Omit<PortalApp, 'id'>>} AppUpdate
 */

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
  const response = await fetch('/api/portal')
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
  const params = new URLSearchParams()
  if (options.includeDisabled) {
    params.set('include_disabled', 'true')
  }
  const query = params.toString()
  const response = await fetch(`/api/apps${query ? `?${query}` : ''}`)
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
  const response = await fetch('/api/apps', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
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
  const response = await fetch(`/api/apps/${encodeURIComponent(id)}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
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
  const response = await fetch(`/api/apps/${encodeURIComponent(id)}`, {
    method: 'DELETE',
  })
  if (!response.ok) {
    throw new Error(await readError(response, 'Failed to delete app'))
  }
}
