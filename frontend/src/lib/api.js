/**
 * @typedef {{ id: string, name: string, description: string, url: string, icon: string, category: string, color: string, order: number, enabled: boolean }} PortalApp
 * @typedef {{ company: string, tagline: string }} PortalInfo
 */

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
 * @returns {Promise<PortalApp[]>}
 */
export async function fetchApps() {
  const response = await fetch('/api/apps')
  if (!response.ok) {
    throw new Error('Failed to load applications')
  }
  return response.json()
}
