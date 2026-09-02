const API_BASE = import.meta.env.VITE_API_BASE_URL ?? ''

async function requestJson(path, options = {}) {
  const { headers: customHeaders = {}, method: customMethod = 'GET', ...restOptions } = options
  const method = customMethod.toUpperCase()
  const response = await fetch(`${API_BASE}${path}`, {
    ...restOptions,
    method,
    headers: {
      'Content-Type': 'application/json',
      ...authHeaders(),
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
  login(username, password) {
    return requestJson('/api/auth/login', { method: 'POST', body: JSON.stringify({ username, password }) })
  },
  listPortalProjects() {
    return requestJson('/api/portal/projects', { headers: authHeaders() })
  },
  listPortalCiDeliveries() {
    return requestJson('/api/portal/ci-deliveries', { headers: authHeaders() })
  },
  listMilestones(projectName) {
    return requestJson(`/api/projects/${encodeURIComponent(projectName)}/milestones`, { headers: authHeaders() })
  },
  updateMilestone(projectName, key, payload) {
    return requestJson(`/api/projects/${encodeURIComponent(projectName)}/milestones/${encodeURIComponent(key)}`, { method: 'PUT', headers: authHeaders(), body: JSON.stringify(payload) })
  },
  listAfterSalesLogs() {
    return requestJson('/api/after-sales/logs', { headers: authHeaders() })
  },
  createAfterSalesLog(payload) {
    return requestJson('/api/after-sales/logs', { method: 'POST', headers: authHeaders(), body: JSON.stringify(payload) })
  },
  updateAfterSalesLog(id, payload) {
    return requestJson(`/api/after-sales/logs/${encodeURIComponent(String(id))}`, { method: 'PUT', headers: authHeaders(), body: JSON.stringify(payload) })
  },
  deleteAfterSalesLog(id) {
    return requestJson(`/api/after-sales/logs/${encodeURIComponent(String(id))}`, { method: 'DELETE', headers: authHeaders() })
  },
  exportAfterSalesLogs() {
    return `${API_BASE}/api/after-sales/logs/export`
  },
  listLogisticsShipments(filters = {}) {
    const query = new URLSearchParams()
    Object.entries(filters).forEach(([key, value]) => {
      if (value) query.set(key, value)
    })
    const suffix = query.toString()
    return requestJson(`/api/logistics/shipments${suffix ? `?${suffix}` : ''}`, { headers: authHeaders() })
  },
  createLogisticsShipment(payload) {
    return requestJson('/api/logistics/shipments', { method: 'POST', headers: authHeaders(), body: JSON.stringify(payload) })
  },
  updateLogisticsShipment(id, payload) {
    return requestJson(`/api/logistics/shipments/${encodeURIComponent(String(id))}`, { method: 'PUT', headers: authHeaders(), body: JSON.stringify(payload) })
  },
  deleteLogisticsShipment(id) {
    return requestJson(`/api/logistics/shipments/${encodeURIComponent(String(id))}`, { method: 'DELETE', headers: authHeaders() })
  },
  listEmpowermentRecords() {
    return requestJson('/api/empowerment/records', { headers: authHeaders() })
  },
  createEmpowermentRecord(payload) {
    return requestJson('/api/empowerment/records', { method: 'POST', headers: authHeaders(), body: JSON.stringify(payload) })
  },
  updateEmpowermentRecord(id, payload) {
    return requestJson(`/api/empowerment/records/${encodeURIComponent(String(id))}`, { method: 'PUT', headers: authHeaders(), body: JSON.stringify(payload) })
  },
  deleteEmpowermentRecord(id) {
    return requestJson(`/api/empowerment/records/${encodeURIComponent(String(id))}`, { method: 'DELETE', headers: authHeaders() })
  },
  listTickets(filters = {}) {
    const query = new URLSearchParams()
    Object.entries(filters).forEach(([key, value]) => {
      if (value) query.set(key, value)
    })
    const suffix = query.toString()
    return requestJson(`/api/customer/tickets${suffix ? `?${suffix}` : ''}`, { headers: authHeaders() })
  },
  createTicket(payload) {
    return requestJson('/api/customer/tickets', { method: 'POST', headers: authHeaders(), body: JSON.stringify(payload) })
  },
  updateTicket(id, payload) {
    return requestJson(`/api/customer/tickets/${encodeURIComponent(String(id))}`, { method: 'PATCH', headers: authHeaders(), body: JSON.stringify(payload) })
  },
  listUsers() {
    return requestJson('/api/admin/users', { headers: authHeaders() })
  },
  createUser(payload) {
    return requestJson('/api/admin/users', { method: 'POST', headers: authHeaders(), body: JSON.stringify(payload) })
  },
  updateUser(id, payload) {
    return requestJson(`/api/admin/users/${encodeURIComponent(String(id))}`, { method: 'PUT', headers: authHeaders(), body: JSON.stringify(payload) })
  },
  deleteUser(id) {
    return requestJson(`/api/admin/users/${encodeURIComponent(String(id))}`, { method: 'DELETE', headers: authHeaders() })
  },
  listFaultComponents(includeInactive = false) {
    const suffix = includeInactive ? '?include_inactive=true' : ''
    return requestJson(`/api/config/fault-components${suffix}`, { headers: authHeaders() })
  },
  createFaultComponent(payload) {
    return requestJson('/api/config/fault-components', { method: 'POST', headers: authHeaders(), body: JSON.stringify(payload) })
  },
  updateFaultComponent(id, payload) {
    return requestJson(`/api/config/fault-components/${encodeURIComponent(String(id))}`, { method: 'PUT', headers: authHeaders(), body: JSON.stringify(payload) })
  },
  deleteFaultComponent(id) {
    return requestJson(`/api/config/fault-components/${encodeURIComponent(String(id))}`, { method: 'DELETE', headers: authHeaders() })
  },
  uploadImage(file) {
    const formData = new FormData()
    formData.append('file', file)
    return fetch(`${API_BASE}/api/upload`, {
      method: 'POST',
      headers: {
        ...authHeaders(),
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
  createAfterSalesFaultCode(payload) {
    return requestJson('/api/after-sales/fault-codes', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  },
  updateAfterSalesFaultCode(id, payload) {
    return requestJson(`/api/after-sales/fault-codes/${encodeURIComponent(String(id))}`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    })
  },
  deleteAfterSalesFaultCode(id) {
    return requestJson(`/api/after-sales/fault-codes/${encodeURIComponent(String(id))}`, {
      method: 'DELETE',
    })
  },
  listTechnicalDocs({ product = '', category = '' } = {}) {
    const query = new URLSearchParams()
    if (product) {
      query.set('product', product)
    }
    if (category) {
      query.set('category', category)
    }
    const suffix = query.toString()
    return requestJson(`/api/technical-docs${suffix ? `?${suffix}` : ''}`)
  },
  uploadTechnicalDoc(formData) {
    return fetch(`${API_BASE}/api/technical-docs`, {
      method: 'POST',
      headers: {
        ...authHeaders(),
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
  updateTechnicalDoc(id, payload) {
    return requestJson(`/api/technical-docs/${encodeURIComponent(String(id))}`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    })
  },
  deleteTechnicalDoc(id) {
    return requestJson(`/api/technical-docs/${encodeURIComponent(String(id))}`, {
      method: 'DELETE',
    })
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

function authHeaders() {
  if (typeof window === 'undefined') return {}
  const token = window.localStorage.getItem('token')
  return token ? { Authorization: `Bearer ${token}` } : {}
}
