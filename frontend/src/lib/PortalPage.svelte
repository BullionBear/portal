<script>
  import { onMount } from 'svelte'
  import { fetchApps, fetchPortalInfo } from './api.js'
  import { handleLinkClick } from './router.js'
  import AppCard from './AppCard.svelte'

  /** @type {import('./api.js').PortalInfo} */
  let portal = $state({
    company: 'Lynkora',
    tagline: 'Company applications at a glance',
  })
  /** @type {import('./api.js').PortalApp[]} */
  let apps = $state([])
  let query = $state('')
  let activeCategory = $state('All')
  let loading = $state(true)
  let error = $state(/** @type {string | null} */ (null))

  onMount(async () => {
    try {
      const [info, list] = await Promise.all([fetchPortalInfo(), fetchApps()])
      portal = info
      apps = list
    } catch (err) {
      error = err instanceof Error ? err.message : 'Unable to load portal'
    } finally {
      loading = false
    }
  })

  let categories = $derived([
    'All',
    ...Array.from(new Set(apps.map((app) => app.category))).sort(),
  ])

  let filtered = $derived(
    apps.filter((app) => {
      const matchesCategory =
        activeCategory === 'All' || app.category === activeCategory
      const haystack = `${app.name} ${app.description} ${app.category}`.toLowerCase()
      const matchesQuery = haystack.includes(query.trim().toLowerCase())
      return matchesCategory && matchesQuery
    }),
  )
</script>

<div class="shell">
  <div class="atmosphere" aria-hidden="true"></div>

  <header class="hero">
    <p class="brand">{portal.company}</p>
    <h1>Portal</h1>
    <p class="tagline">{portal.tagline}</p>
  </header>

  <section class="controls" aria-label="Filter applications">
    <label class="search">
      <span class="sr-only">Search applications</span>
      <input
        type="search"
        placeholder="Search apps…"
        bind:value={query}
        autocomplete="off"
      />
    </label>

    <div class="filters" role="tablist" aria-label="Categories">
      {#each categories as category}
        <button
          type="button"
          class:active={activeCategory === category}
          onclick={() => (activeCategory = category)}
        >
          {category}
        </button>
      {/each}
    </div>
  </section>

  <main>
    {#if loading}
      <p class="status">Loading applications…</p>
    {:else if error}
      <p class="status error">{error}. Is the API running on port 8000?</p>
    {:else if filtered.length === 0}
      <p class="status">No applications match your filters.</p>
    {:else}
      <div class="grid">
        {#each filtered as app, index (app.id)}
          <AppCard {app} {index} />
        {/each}
      </div>
    {/if}
  </main>

  <footer>
    <span>{portal.company}</span>
    <span class="footer-links">
      <span>Open any card to launch the app</span>
      <a href="/admin" onclick={(e) => handleLinkClick(e, '/admin')}>Admin</a>
    </span>
  </footer>
</div>

<style>
  .shell {
    position: relative;
    min-height: 100vh;
    padding: 2.5rem clamp(1.25rem, 4vw, 3.5rem) 2rem;
    overflow: hidden;
  }

  .atmosphere {
    position: fixed;
    inset: 0;
    z-index: -1;
    background:
      radial-gradient(ellipse 70% 50% at 8% -10%, rgba(196, 163, 90, 0.28), transparent 55%),
      radial-gradient(ellipse 55% 45% at 92% 8%, rgba(62, 110, 140, 0.18), transparent 50%),
      radial-gradient(ellipse 60% 40% at 50% 100%, rgba(11, 31, 51, 0.08), transparent 60%),
      linear-gradient(180deg, #eef2f5 0%, #f7f4ee 48%, #ebe6dc 100%);
  }

  .atmosphere::after {
    content: '';
    position: absolute;
    inset: 0;
    opacity: 0.35;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.45'/%3E%3C/svg%3E");
    mix-blend-mode: soft-light;
    pointer-events: none;
  }

  .hero {
    max-width: 42rem;
    margin-bottom: 2.25rem;
    animation: fade-up 0.7s cubic-bezier(0.22, 1, 0.36, 1) both;
  }

  .brand {
    margin: 0 0 0.35rem;
    font-family: var(--font-display);
    font-size: clamp(2.8rem, 7vw, 4.6rem);
    font-weight: 400;
    letter-spacing: -0.03em;
    line-height: 0.95;
    color: var(--ink);
  }

  h1 {
    margin: 0 0 0.75rem;
    font-family: var(--font-sans);
    font-size: 0.82rem;
    font-weight: 700;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: color-mix(in srgb, var(--gold) 85%, var(--ink));
  }

  .tagline {
    margin: 0;
    max-width: 28rem;
    font-size: 1.05rem;
    line-height: 1.5;
    color: color-mix(in srgb, var(--ink) 70%, transparent);
  }

  .controls {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem 1.25rem;
    align-items: center;
    margin-bottom: 1.75rem;
    animation: fade-up 0.7s cubic-bezier(0.22, 1, 0.36, 1) 0.08s both;
  }

  .search input {
    width: min(22rem, 100vw - 2.5rem);
    padding: 0.75rem 1rem;
    border: 1px solid color-mix(in srgb, var(--ink) 12%, transparent);
    border-radius: 999px;
    background: color-mix(in srgb, #fff 72%, transparent);
    color: var(--ink);
    font: inherit;
    outline: none;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
  }

  .search input:focus {
    border-color: color-mix(in srgb, var(--gold) 55%, transparent);
    box-shadow: 0 0 0 3px color-mix(in srgb, var(--gold) 22%, transparent);
  }

  .filters {
    display: flex;
    flex-wrap: wrap;
    gap: 0.45rem;
  }

  .filters button {
    padding: 0.45rem 0.85rem;
    border: 1px solid transparent;
    border-radius: 999px;
    background: transparent;
    color: color-mix(in srgb, var(--ink) 65%, transparent);
    font: inherit;
    font-size: 0.85rem;
    font-weight: 600;
    cursor: pointer;
    transition:
      background 0.2s ease,
      color 0.2s ease,
      border-color 0.2s ease;
  }

  .filters button:hover {
    color: var(--ink);
    background: color-mix(in srgb, #fff 55%, transparent);
  }

  .filters button.active {
    color: var(--ink);
    background: color-mix(in srgb, #fff 80%, transparent);
    border-color: color-mix(in srgb, var(--ink) 12%, transparent);
  }

  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(min(100%, 18.5rem), 1fr));
    gap: 1rem;
  }

  .status {
    margin: 2rem 0;
    color: color-mix(in srgb, var(--ink) 65%, transparent);
  }

  .status.error {
    color: #8a2f2f;
  }

  footer {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    gap: 0.5rem 1.5rem;
    margin-top: 3rem;
    padding-top: 1.25rem;
    border-top: 1px solid color-mix(in srgb, var(--ink) 10%, transparent);
    font-size: 0.82rem;
    color: color-mix(in srgb, var(--ink) 48%, transparent);
  }

  .footer-links {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem 1.25rem;
    align-items: center;
  }

  .footer-links a {
    color: color-mix(in srgb, var(--ink) 55%, transparent);
    text-decoration: none;
    font-weight: 600;
  }

  .footer-links a:hover {
    color: var(--ink);
  }

  .sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
  }

  @keyframes fade-up {
    from {
      opacity: 0;
      transform: translateY(10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
</style>
