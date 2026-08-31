const API_BASE_URL = 'https://deal-drop-jp5q.onrender.com'

function extractErrorMessage(data) {
  if (!data) {
    return 'Something went wrong'
  }

  // Normal FastAPI HTTPException
  if (typeof data.detail === 'string') {
    return data.detail
  }

  // FastAPI validation errors
  if (Array.isArray(data.detail)) {
    return data.detail
      .map((error) => {
        if (typeof error === 'string') {
          return error
        }

        if (error?.msg) {
          return error.msg
        }

        return JSON.stringify(error)
      })
      .join(', ')
  }

  if (data.message) {
    return typeof data.message === 'string'
      ? data.message
      : JSON.stringify(data.message)
  }

  return 'Something went wrong'
}

export async function apiRequest(endpoint, options = {}) {
  const token = localStorage.getItem('access_token')

  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  }

  if (token) {
    headers.Authorization = `Bearer ${token}`
  }

  const response = await fetch(
    `${API_BASE_URL}${endpoint}`,
    {
      ...options,
      headers,
    }
  )

  const data = await response.json().catch(() => null)

  if (!response.ok) {
    throw new Error(
      extractErrorMessage(data)
    )
  }

  return data
}
