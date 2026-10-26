// Free OpenStreetMap tiles (no API key). Override via env to use another provider.
export const MAP_TILE_URL =
  import.meta.env.VITE_MAP_TILE_URL || 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'

export const MAP_TILE_ATTRIBUTION =
  import.meta.env.VITE_MAP_TILE_ATTRIBUTION ||
  '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'

export const MAP_TILE_SUBDOMAINS = import.meta.env.VITE_MAP_TILE_SUBDOMAINS || 'abc'

export const MAP_DEFAULT_CENTER = [30, 20]
export const MAP_DEFAULT_ZOOM = 2
