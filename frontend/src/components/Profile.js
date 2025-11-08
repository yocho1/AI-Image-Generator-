import React, { useState, useEffect } from 'react'
import { imageAPI } from '../services/api'

const Profile = ({ user, onLogout }) => {
  const [images, setImages] = useState([])
  const [favorites, setFavorites] = useState([])
  const [stats, setStats] = useState({})
  const [activeTab, setActiveTab] = useState('images')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchUserData()
  }, [])

  const fetchUserData = async () => {
    try {
      setLoading(true)
      const [imagesRes, favoritesRes, statsRes] = await Promise.all([
        imageAPI.getImages(),
        imageAPI.getFavorites(),
        imageAPI.getStats(),
      ])

      setImages(imagesRes.data.images || [])
      setFavorites(favoritesRes.data.favorites || [])
      setStats(statsRes.data.stats || {})
    } catch (error) {
      console.error('Failed to fetch user data:', error)
    } finally {
      setLoading(false)
    }
  }

  const removeFromFavorites = async (imageId) => {
    try {
      await imageAPI.removeFavorite(imageId)
      setFavorites((prev) => prev.filter((fav) => fav.image.id !== imageId))
    } catch (error) {
      console.error('Failed to remove favorite:', error)
    }
  }

  const tabs = [
    { id: 'images', label: 'My Images', count: images.length },
    { id: 'favorites', label: 'Favorites', count: favorites.length },
  ]

  return (
    <div className='min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 py-8 px-4'>
      <div className='max-w-6xl mx-auto'>
        {/* Header */}
        <div className='flex justify-between items-center mb-8'>
          <div>
            <h1 className='text-3xl font-bold bg-gradient-to-r from-primary-600 to-purple-600 bg-clip-text text-transparent'>
              Your Profile
            </h1>
            <p className='text-gray-600'>Welcome back, {user.username}!</p>
          </div>
          <button onClick={onLogout} className='btn-secondary'>
            Sign Out
          </button>
        </div>

        {/* Stats Grid */}
        <div className='grid md:grid-cols-3 gap-6 mb-8'>
          <div className='card text-center'>
            <div className='text-2xl font-bold text-primary-600'>
              {stats.total_images || 0}
            </div>
            <div className='text-sm text-gray-600'>Total Images</div>
          </div>
          <div className='card text-center'>
            <div className='text-2xl font-bold text-green-600'>
              {stats.total_favorites || 0}
            </div>
            <div className='text-sm text-gray-600'>Favorites</div>
          </div>
          <div className='card text-center'>
            <div className='text-2xl font-bold text-purple-600'>
              {stats.total_collections || 0}
            </div>
            <div className='text-sm text-gray-600'>Collections</div>
          </div>
        </div>

        {/* Tabs */}
        <div className='card'>
          <div className='border-b border-gray-200 mb-6'>
            <nav className='-mb-px flex space-x-8'>
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-2 px-1 border-b-2 font-medium text-sm whitespace-nowrap ${
                    activeTab === tab.id
                      ? 'border-primary-500 text-primary-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  {tab.label}
                  <span className='ml-2 bg-gray-100 text-gray-900 py-0.5 px-2 rounded-full text-xs'>
                    {tab.count}
                  </span>
                </button>
              ))}
            </nav>
          </div>

          {loading ? (
            <div className='text-center py-8'>
              <div className='animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto'></div>
              <p className='text-gray-600 mt-2'>Loading...</p>
            </div>
          ) : (
            <>
              {/* Images Tab */}
              {activeTab === 'images' && (
                <div>
                  <h3 className='text-xl font-semibold text-gray-800 mb-4'>
                    Your Generated Images
                  </h3>
                  {images.length === 0 ? (
                    <p className='text-gray-600 text-center py-8'>
                      No images generated yet. Start creating!
                    </p>
                  ) : (
                    <div className='grid md:grid-cols-2 lg:grid-cols-3 gap-6'>
                      {images.map((image) => (
                        <div
                          key={image.id}
                          className='border border-gray-200 rounded-lg overflow-hidden hover:shadow-lg transition-shadow'
                        >
                          <img
                            src={image.image_url}
                            alt={image.improved_prompt}
                            className='w-full h-48 object-cover'
                          />
                          <div className='p-4'>
                            <p className='text-sm text-gray-600 mb-2 line-clamp-2'>
                              <strong>Original:</strong> {image.original_prompt}
                            </p>
                            <p className='text-sm text-gray-800 mb-2 line-clamp-2'>
                              <strong>Enhanced:</strong> {image.improved_prompt}
                            </p>
                            <div className='flex items-center justify-between'>
                              {image.ai_enhanced && (
                                <span className='inline-block bg-primary-100 text-primary-800 text-xs px-2 py-1 rounded'>
                                  AI Enhanced
                                </span>
                              )}
                              <span className='text-xs text-gray-500'>
                                {new Date(
                                  image.created_at
                                ).toLocaleDateString()}
                              </span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Favorites Tab */}
              {activeTab === 'favorites' && (
                <div>
                  <h3 className='text-xl font-semibold text-gray-800 mb-4'>
                    Your Favorite Images
                  </h3>
                  {favorites.length === 0 ? (
                    <p className='text-gray-600 text-center py-8'>
                      No favorites yet. Start adding some!
                    </p>
                  ) : (
                    <div className='grid md:grid-cols-2 lg:grid-cols-3 gap-6'>
                      {favorites.map((favorite) => (
                        <div
                          key={favorite.id}
                          className='border border-gray-200 rounded-lg overflow-hidden hover:shadow-lg transition-shadow'
                        >
                          <img
                            src={favorite.image.image_url}
                            alt={favorite.image.improved_prompt}
                            className='w-full h-48 object-cover'
                          />
                          <div className='p-4'>
                            <p className='text-sm text-gray-600 mb-2 line-clamp-2'>
                              {favorite.image.improved_prompt}
                            </p>
                            <div className='flex items-center justify-between'>
                              <button
                                onClick={() =>
                                  removeFromFavorites(favorite.image.id)
                                }
                                className='text-red-500 hover:text-red-700 text-sm font-medium'
                              >
                                Remove
                              </button>
                              <span className='text-xs text-gray-500'>
                                {new Date(
                                  favorite.added_at
                                ).toLocaleDateString()}
                              </span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}

export default Profile
