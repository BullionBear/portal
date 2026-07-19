<script>
  import { onMount } from 'svelte'
  import AdminPage from './lib/AdminPage.svelte'
  import PortalPage from './lib/PortalPage.svelte'
  import { currentPath } from './lib/router.js'

  let path = $state(currentPath())

  onMount(() => {
    const onPopState = () => {
      path = currentPath()
    }
    window.addEventListener('popstate', onPopState)
    return () => window.removeEventListener('popstate', onPopState)
  })

  let isAdmin = $derived(path === '/admin')
</script>

{#if isAdmin}
  <AdminPage />
{:else}
  <PortalPage />
{/if}
