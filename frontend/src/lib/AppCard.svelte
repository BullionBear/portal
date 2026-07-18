<script>
  import { iconMarkup } from './icons.js'

  /** @type {{ app: import('./api.js').PortalApp, index: number }} */
  let { app, index = 0 } = $props()
</script>

<a
  class="card"
  href={app.url}
  target="_blank"
  rel="noopener noreferrer"
  style={`--accent: ${app.color}; --delay: ${index * 55}ms`}
>
  <div class="icon" style={`color: ${app.color}`} aria-hidden="true">
    {@html `<svg viewBox="0 0 24 24" width="28" height="28" xmlns="http://www.w3.org/2000/svg">${iconMarkup(app.icon)}</svg>`}
  </div>
  <div class="body">
    <div class="meta">
      <span class="category">{app.category}</span>
      <span class="arrow" aria-hidden="true">↗</span>
    </div>
    <h2>{app.name}</h2>
    <p>{app.description}</p>
  </div>
</a>

<style>
  .card {
    --accent: #c4a35a;
    --delay: 0ms;
    position: relative;
    display: grid;
    grid-template-columns: auto 1fr;
    gap: 1.1rem;
    align-items: start;
    padding: 1.35rem 1.4rem;
    text-decoration: none;
    color: inherit;
    border: 1px solid color-mix(in srgb, var(--ink) 10%, transparent);
    background:
      linear-gradient(
        145deg,
        color-mix(in srgb, var(--accent) 10%, var(--surface)) 0%,
        var(--surface) 48%
      );
    border-radius: 18px;
    box-shadow: 0 1px 0 color-mix(in srgb, #fff 55%, transparent) inset;
    transform: translateY(12px);
    opacity: 0;
    animation: rise 0.55s cubic-bezier(0.22, 1, 0.36, 1) forwards;
    animation-delay: var(--delay);
    transition:
      transform 0.25s ease,
      border-color 0.25s ease,
      box-shadow 0.25s ease;
  }

  .card::before {
    content: '';
    position: absolute;
    inset: 0 auto 0 0;
    width: 3px;
    border-radius: 18px 0 0 18px;
    background: var(--accent);
    opacity: 0.85;
  }

  .card:hover,
  .card:focus-visible {
    transform: translateY(-3px);
    border-color: color-mix(in srgb, var(--accent) 45%, transparent);
    box-shadow:
      0 14px 34px color-mix(in srgb, var(--ink) 10%, transparent),
      0 1px 0 color-mix(in srgb, #fff 55%, transparent) inset;
    outline: none;
  }

  .icon {
    display: grid;
    place-items: center;
    width: 3.1rem;
    height: 3.1rem;
    border-radius: 12px;
    background: color-mix(in srgb, var(--accent) 14%, #fff);
  }

  .meta {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.75rem;
    margin-bottom: 0.35rem;
  }

  .category {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: color-mix(in srgb, var(--ink) 52%, transparent);
  }

  .arrow {
    font-size: 0.95rem;
    color: color-mix(in srgb, var(--ink) 40%, transparent);
    transition: transform 0.2s ease, color 0.2s ease;
  }

  .card:hover .arrow,
  .card:focus-visible .arrow {
    color: var(--accent);
    transform: translate(2px, -2px);
  }

  h2 {
    margin: 0 0 0.4rem;
    font-family: var(--font-display);
    font-size: 1.45rem;
    font-weight: 400;
    letter-spacing: -0.02em;
    line-height: 1.15;
  }

  p {
    margin: 0;
    font-size: 0.92rem;
    line-height: 1.45;
    color: color-mix(in srgb, var(--ink) 68%, transparent);
  }

  @keyframes rise {
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
</style>
