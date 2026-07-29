const API_BASE = import.meta.env.VITE_API_BASE_URL ?? ''

async function requestJson(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
    ...options,
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
