import React, { useState, useEffect } from 'react'

const Profile = ({ user, onLogout }) => {
  const [images, setImages] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchUserImages()
  }, [])

  const fetchUserImages = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('http://127.0.0.1:5002/api/images', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        setImages(data.images)
      }
    } catch (error) {
      console.error('Failed to fetch images:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className='min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 py-8 px-4'>
      <div className='max-w-6xl mx-auto'>
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

        <div className='grid md:grid-cols-2 gap-8'>
          {/* User Info */}
          <div className='card'>
            <h3 className='text-xl font-semibold text-gray-800 mb-4'>
              Account Information
            </h3>
            <div className='space-y-3'>
              <div>
                <label className='text-sm font-medium text-gray-600'>
                  Username
                </label>
                <p className='text-gray-800'>{user.username}</p>
              </div>
              <div>
                <label className='text-sm font-medium text-gray-600'>
                  Email
                </label>
                <p className='text-gray-800'>{user.email}</p>
              </div>
              <div>
                <label className='text-sm font-medium text-gray-600'>
                  Member Since
                </label>
                <p className='text-gray-800'>
                  {new Date(user.created_at).toLocaleDateString()}
                </p>
              </div>
            </div>
          </div>

          {/* Image Stats */}
          <div className='card'>
            <h3 className='text-xl font-semibold text-gray-800 mb-4'>
              Generation Stats
            </h3>
            <div className='grid grid-cols-2 gap-4'>
              <div className='text-center p-4 bg-primary-50 rounded-lg'>
                <p className='text-2xl font-bold text-primary-600'>
                  {images.length}
                </p>
                <p className='text-sm text-gray-600'>Total Images</p>
              </div>
              <div className='text-center p-4 bg-green-50 rounded-lg'>
                <p className='text-2xl font-bold text-green-600'>
                  {images.filter((img) => img.ai_enhanced).length}
                </p>
                <p className='text-sm text-gray-600'>AI Enhanced</p>
              </div>
            </div>
          </div>
        </div>

        {/* Image History */}
        <div className='card mt-8'>
          <h3 className='text-xl font-semibold text-gray-800 mb-4'>
            Your Generated Images
          </h3>
          {loading ? (
            <p className='text-gray-600 text-center py-8'>
              Loading your images...
            </p>
          ) : images.length === 0 ? (
            <p className='text-gray-600 text-center py-8'>
              No images generated yet. Start creating!
            </p>
          ) : (
            <div className='grid md:grid-cols-2 lg:grid-cols-3 gap-6'>
              {images.map((image) => (
                <div
                  key={image.id}
                  className='border border-gray-200 rounded-lg overflow-hidden'
                >
                  <img
                    src={image.image_url}
                    alt={image.improved_prompt}
                    className='w-full h-48 object-cover'
                  />
                  <div className='p-4'>
                    <p className='text-sm text-gray-600 mb-2'>
                      <strong>Original:</strong> {image.original_prompt}
                    </p>
                    <p className='text-sm text-gray-800 mb-2'>
                      <strong>Enhanced:</strong> {image.improved_prompt}
                    </p>
                    {image.ai_enhanced && (
                      <span className='inline-block bg-primary-100 text-primary-800 text-xs px-2 py-1 rounded'>
                        AI Enhanced
                      </span>
                    )}
                    <p className='text-xs text-gray-500 mt-2'>
                      {new Date(image.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Profile