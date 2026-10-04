/** Ids of the global panels nanoMuse adds to the harness's `main` seat. */

/** The rooms of the Muse desktop, in the rail's order. */
export const FEED_PANEL = 'nanomuse-feed'
export const IDEAS_PANEL = 'nanomuse-ideas'
export const GOALS_PANEL = 'nanomuse-goals'
export const LIBRARY_PANEL = 'nanomuse-library'

/** The Devices page: this computer on the account's hub and the other devices. */
export const DEVICES_PANEL = 'nanomuse-devices'

export const ROOM_PANELS = [FEED_PANEL, IDEAS_PANEL, GOALS_PANEL, LIBRARY_PANEL, DEVICES_PANEL] as const

/** Where a problem with nanoMuse is reported. */
export const REPO_URL = 'https://github.com/zeeshanhaque21/nanoMuse'
export const ISSUES_URL = 'https://github.com/zeeshanhaque21/nanoMuse/issues'
// The fork's own desktop docs, which exist in this repository. Upstream pointed this at
// a third-party host; this fork links only a page it can actually verify.
export const DOCS_URL = 'https://github.com/zeeshanhaque21/nanoMuse/blob/main/docs/desktop-muse.md'
