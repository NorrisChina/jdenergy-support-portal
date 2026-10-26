// Default basemap: AutoNavi (Gaode) tiles with Chinese labels, no API key.
// Override via env (e.g. back to OpenStreetMap: https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png, subdomains "abc").
export const MAP_TILE_URL =
  import.meta.env.VITE_MAP_TILE_URL ||
  'https://webrd0{s}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}'

export const MAP_TILE_ATTRIBUTION =
  import.meta.env.VITE_MAP_TILE_ATTRIBUTION || '&copy; <a href="https://www.amap.com/">高德地图</a>'

export const MAP_TILE_SUBDOMAINS = import.meta.env.VITE_MAP_TILE_SUBDOMAINS || '1234'
export const MAP_TILE_MAX_ZOOM = Number(import.meta.env.VITE_MAP_TILE_MAX_ZOOM) || 18

export const MAP_DEFAULT_CENTER = [30, 20]
export const MAP_DEFAULT_ZOOM = 2
