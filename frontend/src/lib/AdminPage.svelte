<script>
  import { onMount } from 'svelte'
  import {
    createApp,
    deleteApp,
    fetchApps,
    updateApp,
  } from './api.js'
  import { handleLinkClick } from './router.js'

  const ID_PATTERN = /^[a-z0-9][a-z0-9_-]*$/
  const COLOR_PATTERN = /^#[0-9A-Fa-f]{6}$/

  /** @returns {import('./api.js').PortalApp} */
  function emptyForm() {
    return {
      id: '',
      name: '',
      description: '',
      url: 'https://',
      category: 'General',
      color: '#C4A35A',
      order: 100,
      enabled: true,
    }
  }

  /** @type {import('./api.js').PortalApp[]} */
  let apps = $state([])
  /** @type {import('./api.js').PortalApp} */
  let form = $state(emptyForm())
  let editingId = $state(/** @type {string | null} */ (null))
  let loading = $state(true)
  let saving = $state(false)
  let error = $state(/** @type {string | null} */ (null))
  let notice = $state(/** @type {string | null} */ (null))

  let isEditing = $derived(editingId !== null)

  onMount(() => {
    void loadApps()
  })

  async function loadApps() {
    loading = true
    error = null
    try {
      apps = await fetchApps({ includeDisabled: true })
    } catch (err) {
      error = err instanceof Error ? err.message : 'Unable to load apps'
    } finally {
      loading = false
    }
  }

  /** @param {import('./api.js').PortalApp} app */
  function selectApp(app) {
    editingId = app.id
    form = { ...app }
    notice = null
    error = null
  }

  function startCreate() {
    editingId = null
    form = emptyForm()
    notice = null
    error = null
  }

  /** @returns {string | null} */
  function validate() {
    if (!isEditing) {
      if (!form.id.trim()) return 'ID is required'
      if (!ID_PATTERN.test(form.id.trim())) {
        return 'ID must start with a letter or number and use only a-z, 0-9, _ or -'
      }
    }
    if (!form.name.trim()) return 'Name is required'
    if (!form.description.trim()) return 'Description is required'
    if (!form.url.trim()) return 'URL is required'
    try {
      void new URL(form.url.trim())
    } catch {
      return 'URL must be a valid absolute URL'
    }
    if (!form.category.trim()) return 'Category is required'
    if (!COLOR_PATTERN.test(form.color.trim())) {
      return 'Color must be a hex value like #C4A35A'
    }
    if (!Number.isFinite(form.order) || form.order < 0) {
      return 'Order must be a non-negative number'
    }
    return null
  }

  async function onSubmit(event) {
    event.preventDefault()
    notice = null
    const validationError = validate()
    if (validationError) {
      error = validationError
      return
    }

    saving = true
    error = null
    try {
      if (isEditing && editingId) {
        const updated = await updateApp(editingId, {
          name: form.name.trim(),
          description: form.description.trim(),
          url: form.url.trim(),
          category: form.category.trim(),
          color: form.color.trim(),
          order: Number(form.order),
          enabled: form.enabled,
        })
        apps = apps
          .map((app) => (app.id === editingId ? updated : app))
          .sort((a, b) => a.order - b.order || a.name.localeCompare(b.name))
        form = { ...updated }
        notice = `Updated “${updated.name}”`
      } else {
        const created = await createApp({
          id: form.id.trim(),
          name: form.name.trim(),
          description: form.description.trim(),
          url: form.url.trim(),
          category: form.category.trim(),
          color: form.color.trim(),
          order: Number(form.order),
          enabled: form.enabled,
        })
        apps = [...apps, created].sort(
          (a, b) => a.order - b.order || a.name.localeCompare(b.name),
        )
        selectApp(created)
        notice = `Created “${created.name}”`
      }
    } catch (err) {
      error = err instanceof Error ? err.message : 'Save failed'
    } finally {
      saving = false
    }
  }

  /** @param {import('./api.js').PortalApp} app */
  async function toggleEnabled(app) {
    error = null
    notice = null
    try {
      const updated = await updateApp(app.id, { enabled: !app.enabled })
      apps = apps.map((item) => (item.id === app.id ? updated : item))
      if (editingId === app.id) {
        form = { ...updated }
      }
      notice = updated.enabled
        ? `Enabled “${updated.name}”`
        : `Disabled “${updated.name}”`
    } catch (err) {
      error = err instanceof Error ? err.message : 'Update failed'
    }
  }

  async function onDelete() {
    if (!editingId) return
    const name = form.name || editingId
    if (!confirm(`Delete “${name}”? This cannot be undone.`)) return

    saving = true
    error = null
    notice = null
    try {
      await deleteApp(editingId)
      apps = apps.filter((app) => app.id !== editingId)
      startCreate()
      notice = `Deleted “${name}”`
    } catch (err) {
      error = err instanceof Error ? err.message : 'Delete failed'
    } finally {
      saving = false
    }
  }
</script>

<div class="shell">
  <div class="atmosphere" aria-hidden="true"></div>

  <header class="header">
    <div>
      <p class="eyebrow">Catalog</p>
      <h1>Admin</h1>
      <p class="lede">Add, edit, enable, or remove portal applications.</p>
    </div>
    <a class="back" href="/" onclick={(e) => handleLinkClick(e, '/')}>
      ← Back to portal
    </a>
  </header>

  {#if error}
    <p class="banner error" role="alert">{error}</p>
  {/if}
  {#if notice}
    <p class="banner ok" role="status">{notice}</p>
  {/if}

  <div class="layout">
    <section class="list-panel" aria-label="Applications">
      <div class="panel-head">
        <h2>Apps</h2>
        <button type="button" class="ghost" onclick={startCreate}>New app</button>
      </div>

      {#if loading}
        <p class="muted">Loading…</p>
      {:else if apps.length === 0}
        <p class="muted">No apps yet. Create the first one.</p>
      {:else}
        <ul class="app-list">
          {#each apps as app (app.id)}
            <li>
              <button
                type="button"
                class="app-row"
                class:active={editingId === app.id}
                class:disabled-app={!app.enabled}
                onclick={() => selectApp(app)}
              >
                <span class="swatch" style={`background: ${app.color}`}></span>
                <span class="app-meta">
                  <span class="app-name">{app.name}</span>
                  <span class="app-sub">{app.id} · {app.category} · #{app.order}</span>
                </span>
                <span class="badge" class:off={!app.enabled}>
                  {app.enabled ? 'On' : 'Off'}
                </span>
              </button>
              <button
                type="button"
                class="toggle"
                onclick={() => toggleEnabled(app)}
                title={app.enabled ? 'Disable' : 'Enable'}
              >
                {app.enabled ? 'Disable' : 'Enable'}
              </button>
            </li>
          {/each}
        </ul>
      {/if}
    </section>

    <section class="form-panel" aria-label="App editor">
      <div class="panel-head">
        <h2>{isEditing ? 'Edit app' : 'New app'}</h2>
      </div>

      <form onsubmit={onSubmit}>
        <label>
          <span>ID</span>
          <input
            bind:value={form.id}
            disabled={isEditing || saving}
            placeholder="cpanel"
            autocomplete="off"
            required={!isEditing}
          />
        </label>

        <label>
          <span>Name</span>
          <input bind:value={form.name} disabled={saving} required />
        </label>

        <label>
          <span>Description</span>
          <textarea
            bind:value={form.description}
            disabled={saving}
            rows="3"
            required
          ></textarea>
        </label>

        <label>
          <span>URL</span>
          <input
            type="url"
            bind:value={form.url}
            disabled={saving}
            placeholder="https://example.com"
            required
          />
        </label>

        <div class="row">
          <label>
            <span>Category</span>
            <input bind:value={form.category} disabled={saving} required />
          </label>
          <label>
            <span>Order</span>
            <input
              type="number"
              min="0"
              step="1"
              bind:value={form.order}
              disabled={saving}
              required
            />
          </label>
        </div>

        <div class="row">
          <label class="color-field">
            <span>Color</span>
            <div class="color-inputs">
              <input
                type="color"
                value={COLOR_PATTERN.test(form.color) ? form.color : '#C4A35A'}
                disabled={saving}
                oninput={(e) => {
                  form.color = /** @type {HTMLInputElement} */ (e.currentTarget).value
                }}
              />
              <input
                bind:value={form.color}
                disabled={saving}
                placeholder="#C4A35A"
                required
              />
            </div>
          </label>
          <label class="check">
            <input type="checkbox" bind:checked={form.enabled} disabled={saving} />
            <span>Enabled</span>
          </label>
        </div>

        <div class="actions">
          <button type="submit" class="primary" disabled={saving}>
            {saving ? 'Saving…' : isEditing ? 'Save changes' : 'Create app'}
          </button>
          {#if isEditing}
            <button
              type="button"
              class="danger"
              disabled={saving}
              onclick={onDelete}
            >
              Delete
            </button>
          {/if}
        </div>
      </form>
    </section>
  </div>
</div>

<style>
  .shell {
    position: relative;
    min-height: 100vh;
    padding: 2rem clamp(1.25rem, 4vw, 3rem) 2.5rem;
  }

  .atmosphere {
    position: fixed;
    inset: 0;
    z-index: -1;
    background:
      radial-gradient(ellipse 70% 50% at 8% -10%, rgba(196, 163, 90, 0.22), transparent 55%),
      radial-gradient(ellipse 55% 45% at 92% 8%, rgba(62, 110, 140, 0.14), transparent 50%),
      linear-gradient(180deg, #eef2f5 0%, #f7f4ee 48%, #ebe6dc 100%);
  }

  .header {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    gap: 1rem 2rem;
    align-items: flex-end;
    margin-bottom: 1.5rem;
  }

  .eyebrow {
    margin: 0 0 0.35rem;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: color-mix(in srgb, var(--gold) 85%, var(--ink));
  }

  h1 {
    margin: 0 0 0.4rem;
    font-family: var(--font-display);
    font-size: clamp(2.2rem, 5vw, 3rem);
    font-weight: 400;
    letter-spacing: -0.02em;
    line-height: 1;
  }

  .lede {
    margin: 0;
    color: color-mix(in srgb, var(--ink) 68%, transparent);
  }

  .back {
    color: color-mix(in srgb, var(--ink) 65%, transparent);
    text-decoration: none;
    font-weight: 600;
    font-size: 0.9rem;
  }

  .back:hover {
    color: var(--ink);
  }

  .banner {
    margin: 0 0 1rem;
    padding: 0.75rem 1rem;
    border-radius: 10px;
    font-size: 0.92rem;
  }

  .banner.error {
    background: color-mix(in srgb, #8a2f2f 12%, #fff);
    color: #8a2f2f;
  }

  .banner.ok {
    background: color-mix(in srgb, #2f6b45 12%, #fff);
    color: #2f6b45;
  }

  .layout {
    display: grid;
    grid-template-columns: minmax(16rem, 22rem) minmax(0, 1fr);
    gap: 1.25rem;
    align-items: start;
  }

  @media (max-width: 860px) {
    .layout {
      grid-template-columns: 1fr;
    }
  }

  .list-panel,
  .form-panel {
    padding: 1.15rem 1.25rem 1.35rem;
    border: 1px solid color-mix(in srgb, var(--ink) 10%, transparent);
    border-radius: 16px;
    background: var(--surface);
    backdrop-filter: blur(8px);
  }

  .panel-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1rem;
  }

  h2 {
    margin: 0;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: color-mix(in srgb, var(--ink) 55%, transparent);
  }

  .muted {
    margin: 0;
    color: color-mix(in srgb, var(--ink) 55%, transparent);
  }

  .app-list {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 0.45rem;
  }

  .app-list li {
    display: grid;
    grid-template-columns: 1fr auto;
    gap: 0.35rem;
  }

  .app-row {
    display: grid;
    grid-template-columns: auto 1fr auto;
    gap: 0.7rem;
    align-items: center;
    width: 100%;
    padding: 0.65rem 0.75rem;
    border: 1px solid transparent;
    border-radius: 12px;
    background: color-mix(in srgb, #fff 55%, transparent);
    color: inherit;
    text-align: left;
    cursor: pointer;
  }

  .app-row:hover {
    border-color: color-mix(in srgb, var(--ink) 12%, transparent);
  }

  .app-row.active {
    border-color: color-mix(in srgb, var(--gold) 55%, transparent);
    background: color-mix(in srgb, var(--gold) 12%, #fff);
  }

  .app-row.disabled-app .app-name {
    opacity: 0.65;
  }

  .swatch {
    width: 0.85rem;
    height: 0.85rem;
    border-radius: 999px;
  }

  .app-meta {
    display: flex;
    flex-direction: column;
    gap: 0.15rem;
    min-width: 0;
  }

  .app-name {
    font-weight: 650;
    font-size: 0.95rem;
  }

  .app-sub {
    font-size: 0.72rem;
    color: color-mix(in srgb, var(--ink) 50%, transparent);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .badge {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: #2f6b45;
  }

  .badge.off {
    color: color-mix(in srgb, var(--ink) 45%, transparent);
  }

  .toggle,
  .ghost,
  .primary,
  .danger {
    border-radius: 10px;
    border: 1px solid color-mix(in srgb, var(--ink) 12%, transparent);
    background: #fff;
    color: var(--ink);
    font: inherit;
    font-size: 0.82rem;
    font-weight: 600;
    cursor: pointer;
    padding: 0.45rem 0.75rem;
  }

  .toggle {
    align-self: center;
  }

  .ghost:hover,
  .toggle:hover {
    border-color: color-mix(in srgb, var(--ink) 22%, transparent);
  }

  .primary {
    background: var(--ink);
    color: #fff;
    border-color: var(--ink);
  }

  .primary:hover:not(:disabled) {
    background: color-mix(in srgb, var(--ink) 88%, #fff);
  }

  .danger {
    color: #8a2f2f;
    border-color: color-mix(in srgb, #8a2f2f 35%, transparent);
    background: color-mix(in srgb, #8a2f2f 6%, #fff);
  }

  .primary:disabled,
  .danger:disabled,
  .toggle:disabled {
    opacity: 0.55;
    cursor: not-allowed;
  }

  form {
    display: flex;
    flex-direction: column;
    gap: 0.85rem;
  }

  label {
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
    font-size: 0.78rem;
    font-weight: 650;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    color: color-mix(in srgb, var(--ink) 58%, transparent);
  }

  input,
  textarea {
    width: 100%;
    padding: 0.65rem 0.75rem;
    border: 1px solid color-mix(in srgb, var(--ink) 12%, transparent);
    border-radius: 10px;
    background: #fff;
    color: var(--ink);
    font: inherit;
    font-size: 0.95rem;
    font-weight: 500;
    letter-spacing: 0;
    text-transform: none;
    outline: none;
  }

  input:focus,
  textarea:focus {
    border-color: color-mix(in srgb, var(--gold) 55%, transparent);
    box-shadow: 0 0 0 3px color-mix(in srgb, var(--gold) 20%, transparent);
  }

  input:disabled,
  textarea:disabled {
    background: color-mix(in srgb, var(--ink) 4%, #fff);
    color: color-mix(in srgb, var(--ink) 55%, transparent);
  }

  .row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.85rem;
  }

  @media (max-width: 560px) {
    .row {
      grid-template-columns: 1fr;
    }
  }

  .color-inputs {
    display: grid;
    grid-template-columns: 3rem 1fr;
    gap: 0.5rem;
    align-items: center;
  }

  .color-inputs input[type='color'] {
    padding: 0.2rem;
    height: 2.55rem;
    cursor: pointer;
  }

  .check {
    flex-direction: row;
    align-items: center;
    gap: 0.55rem;
    align-self: end;
    padding-bottom: 0.55rem;
    text-transform: none;
    letter-spacing: 0;
    font-size: 0.95rem;
    font-weight: 600;
    color: var(--ink);
  }

  .check input {
    width: auto;
    accent-color: var(--ink);
  }

  .actions {
    display: flex;
    flex-wrap: wrap;
    gap: 0.6rem;
    margin-top: 0.35rem;
  }
</style>
