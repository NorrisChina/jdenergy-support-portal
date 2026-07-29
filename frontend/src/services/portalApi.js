const API_BASE = import.meta.env.VITE_API_BASE_URL ?? ''

function readInternalModeFlag() {
  if (typeof window === 'undefined') {
    return false
  }
  return window.localStorage.getItem('isInternalMode') === 'true' || window.localStorage.getItem('jd-energy.staff-mode') === 'true'
}

function buildInternalModeHeaders(method = 'GET') {
  const normalizedMethod = method.toUpperCase()
  if (!['POST', 'PUT', 'PATCH', 'DELETE'].includes(normalizedMethod)) {
    return {}
  }
  return {
    'x-internal-mode': readInternalModeFlag() ? 'true' : 'false',
  }
}

async function requestJson(path, options = {}) {
  const { headers: customHeaders = {}, method: customMethod = 'GET', ...restOptions } = options
  const method = customMethod.toUpperCase()
  const response = await fetch(`${API_BASE}${path}`, {
    ...restOptions,
    method,
    headers: {
      'Content-Type': 'application/json',
      ...buildInternalModeHeaders(method),
      ...customHeaders,
    },
  })

  const contentType = response.headers.get('content-type') ?? ''
  const payload = contentType.includes('application/json') ? await response.json() : await response.text()

  if (!response.ok) {
    const detail = typeof payload === 'object' && payload !== null && 'detail' in payload ? payload.detail : payload
    throw new Error(typeof detail === 'string' ? detail : `HTTP ${response.status}`)
  }

  return payload
}

export const portalApi = {
  uploadImage(file) {
    const formData = new FormData()
    formData.append('file', file)
    return fetch(`${API_BASE}/api/upload`, {
      method: 'POST',
      headers: {
        ...buildInternalModeHeaders('POST'),
      },
      body: formData,
    }).then(async (response) => {
      const text = await response.text()
      let payload = {}
      if (text) {
        try {
          payload = JSON.parse(text)
        } catch {
          payload = { detail: text }
        }
      }
      if (!response.ok) {
        throw new Error(payload?.detail ?? `HTTP ${response.status}`)
      }
      return payload
    })
  },
  getFaultCodes(query = '') {
    return requestJson(`/api/fault-codes?q=${encodeURIComponent(query)}`)
  },
  listAfterSalesFaultCodes({ page = 1, pageSize = 20, module = '', keyword = '' } = {}) {
    const query = new URLSearchParams()
    query.set('page', String(page))
    query.set('page_size', String(pageSize))
    if (module) {
      query.set('module', module)
    }
    if (keyword) {
      query.set('keyword', keyword)
    }
    return requestJson(`/api/after-sales/fault-codes?${query.toString()}`)
  },
  createFaultCode(payload) {
    return requestJson('/api/fault-codes', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  },
  updateFaultCode(faultCode, payload) {
    return requestJson(`/api/fault-codes/${encodeURIComponent(faultCode)}`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    })
  },
  deleteFaultCode(faultCode) {
    return requestJson(`/api/fault-codes/${encodeURIComponent(faultCode)}`, {
      method: 'DELETE',
    })
  },
  listGridProjects() {
    return requestJson('/api/ledger/grid-scale')
  },
  createGridProject(payload) {
    return requestJson('/api/ledger/grid-scale', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  },
  updateGridProject(projectName, payload) {
    return requestJson(`/api/ledger/grid-scale/${encodeURIComponent(projectName)}`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    })
  },
  deleteGridProject(projectName) {
    return requestJson(`/api/ledger/grid-scale/${encodeURIComponent(projectName)}`, {
      method: 'DELETE',
    })
  },
  updateGridProjectStatus(projectName, progressStatus) {
    return requestJson(`/api/ledger/grid-scale/${encodeURIComponent(projectName)}/status`, {
      method: 'POST',
      body: JSON.stringify({ progress_status: progressStatus }),
    })
  },
  listCiDeliveries() {
    return requestJson('/api/ledger/ci-deliveries')
  },
  createCiDelivery(payload) {
    return requestJson('/api/ledger/ci-deliveries', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  },
  updateCiDelivery(dealerName, payload) {
    return requestJson(`/api/ledger/ci-deliveries/${encodeURIComponent(dealerName)}`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    })
  },
  deleteCiDelivery(dealerName) {
    return requestJson(`/api/ledger/ci-deliveries/${encodeURIComponent(dealerName)}`, {
      method: 'DELETE',
    })
  },
  getWarehouseSummary(warehouseName) {
    return requestJson(`/api/warehouse/summary?warehouse_name=${encodeURIComponent(warehouseName)}`)
  },
  createWarehouseTransaction(payload) {
    return requestJson('/api/warehouse/transactions', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  },
  updateWarehouseTransaction(txNo, payload) {
    return requestJson(`/api/warehouse/transactions/${encodeURIComponent(txNo)}`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    })
  },
  deleteWarehouseTransaction(txNo) {
    return requestJson(`/api/warehouse/transactions/${encodeURIComponent(txNo)}`, {
      method: 'DELETE',
    })
  },
  listWarehouseInventory() {
    return requestJson('/api/warehouse/inventory')
  },
  createWarehouseInventoryItem(payload) {
    return requestJson('/api/warehouse/inventory', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  },
  updateWarehouseInventoryItem(itemNo, payload) {
    return requestJson(`/api/warehouse/inventory/${encodeURIComponent(itemNo)}`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    })
  },
  deleteWarehouseInventoryItem(itemNo) {
    return requestJson(`/api/warehouse/inventory/${encodeURIComponent(itemNo)}`, {
      method: 'DELETE',
    })
  },
}
