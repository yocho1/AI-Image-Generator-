import axios from 'axios'

const API_BASE_URL = 'http://127.0.0.1:5002/api'

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add token to requests automatically
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Handle token expiration
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.reload()
    }
    return Promise.reject(error)
  }
)

export const authAPI = {
  register: (userData) => api.post('/register', userData),
  login: (userData) => api.post('/login', userData),
  getProfile: () => api.get('/profile'),
}

export const imageAPI = {
  generate: (promptData) => api.post('/generate', promptData),
  getImages: (page = 1, per_page = 10) =>
    api.get('/images', { params: { page, per_page } }),
  addFavorite: (imageId) => api.post('/favorites', { image_id: imageId }),
  removeFavorite: (imageId) => api.delete(`/favorites/${imageId}`),
  getFavorites: (page = 1, per_page = 10) =>
    api.get('/favorites', { params: { page, per_page } }),
  getStats: () => api.get('/stats'),
}

export default api
