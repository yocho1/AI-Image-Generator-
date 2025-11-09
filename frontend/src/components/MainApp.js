import React, { useState } from 'react'
import { imageAPI } from '../services/api'

// SVG Icons (keep your existing icons)
const Sparkles = () => (
  <svg
    className='w-6 h-6'
    fill='none'
    stroke='currentColor'
    viewBox='0 0 24 24'
  >
    <path
      strokeLinecap='round'
      strokeLinejoin='round'
      strokeWidth={2}
      d='M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z'
    />
  </svg>
)

const Download = () => (
  <svg
    className='w-5 h-5'
    fill='none'
    stroke='currentColor'
    viewBox='0 0 24 24'
  >
    <path
      strokeLinecap='round'
      strokeLinejoin='round'
      strokeWidth={2}
      d='M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z'
    />
  </svg>
)

const RefreshCw = () => (
  <svg
    className='w-5 h-5'
    fill='none'
    stroke='currentColor'
    viewBox='0 0 24 24'
  >
    <path
      strokeLinecap='round'
      strokeLinejoin='round'
      strokeWidth={2}
      d='M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15'
    />
  </svg>
)

const ImageIcon = () => (
  <svg
    className='w-6 h-6'
    fill='none'
    stroke='currentColor'
    viewBox='0 0 24 24'
  >
    <path
      strokeLinecap='round'
      strokeLinejoin='round'
      strokeWidth={2}
      d='M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z'
    />
  </svg>
)

const Zap = () => (
  <svg
    className='w-5 h-5'
    fill='none'
    stroke='currentColor'
    viewBox='0 0 24 24'
  >
    <path
      strokeLinecap='round'
      strokeLinejoin='round'
      strokeWidth={2}
      d='M13 10V3L4 14h7v7l9-11h-7z'
    />
  </svg>
)

const Heart = ({ filled = false }) => (
  <svg
    className={`w-5 h-5 ${
      filled ? 'text-red-500 fill-current' : 'text-gray-400'
    }`}
    viewBox='0 0 24 24'
  >
    <path
      strokeLinecap='round'
      strokeLinejoin='round'
      strokeWidth={2}
      d='M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z'
    />
  </svg>
)

const MainApp = ({ user }) => {
  const [prompt, setPrompt] = useState('')
  const [style, setStyle] = useState('realistic')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  const generateImage = async () => {
    if (!prompt.trim()) {
      setError('Please enter a prompt')
      return
    }

    setLoading(true)
    setError('')
    setResult(null)

    try {
      const response = await imageAPI.generate({
        prompt: prompt.trim(),
        style: style,
      })

      setResult(response.data)
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to generate image')
    } finally {
      setLoading(false)
    }
  }

  const addToFavorites = async (imageId) => {
    try {
      await imageAPI.addFavorite(imageId)
      setResult((prev) => ({
        ...prev,
        is_favorite: true,
      }))
    } catch (err) {
      console.error('Failed to add to favorites:', err)
    }
  }

  const removeFromFavorites = async (imageId) => {
    try {
      await imageAPI.removeFavorite(imageId)
      setResult((prev) => ({
        ...prev,
        is_favorite: false,
      }))
    } catch (err) {
      console.error('Failed to remove from favorites:', err)
    }
  }

  const resetForm = () => {
    setPrompt('')
    setResult(null)
    setError('')
  }

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text)
    alert('Copied to clipboard!')
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      generateImage()
    }
  }

  const styles = [
    { value: 'realistic', label: 'Realistic' },
    { value: 'anime', label: 'Anime' },
    { value: 'painting', label: 'Painting' },
    { value: 'cartoon', label: 'Cartoon' },
    { value: 'minimalist', label: 'Minimalist' },
  ]

  return (
    <div className='min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 py-8 px-4'>
      <div className='max-w-6xl mx-auto'>
        {/* Header */}
        <div className='text-center mb-12'>
          <div className='flex items-center justify-center gap-3 mb-4'>
            <div className='p-3 bg-gradient-to-r from-primary-500 to-purple-600 rounded-2xl'>
              <Sparkles />
            </div>
            <h1 className='text-4xl md:text-5xl font-bold bg-gradient-to-r from-primary-600 to-purple-600 bg-clip-text text-transparent'>
              AI Image Generator
            </h1>
          </div>
          <p className='text-gray-600 text-lg max-w-2xl mx-auto'>
            Welcome back, {user.username}! Transform your ideas into stunning
            visual concepts
          </p>
        </div>

        <div className='grid lg:grid-cols-2 gap-8'>
          {/* Input Section */}
          <div className='space-y-6'>
            <div className='card'>
              <div className='flex items-center gap-2 mb-4'>
                <Zap />
                <h2 className='text-xl font-semibold text-gray-800'>
                  Create Your Vision
                </h2>
              </div>

              <div className='space-y-4'>
                <div>
                  <label className='block text-sm font-medium text-gray-700 mb-2'>
                    Describe your image
                  </label>
                  <textarea
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder='A cute baby in panda costume, professional photo...'
                    className='input-field h-32 resize-none'
                    disabled={loading}
                  />
                </div>

                <div>
                  <label className='block text-sm font-medium text-gray-700 mb-2'>
                    Style
                  </label>
                  <select
                    value={style}
                    onChange={(e) => setStyle(e.target.value)}
                    className='input-field'
                    disabled={loading}
                  >
                    {styles.map((styleOption) => (
                      <option key={styleOption.value} value={styleOption.value}>
                        {styleOption.label}
                      </option>
                    ))}
                  </select>
                </div>

                <button
                  onClick={generateImage}
                  disabled={loading || !prompt.trim()}
                  className='btn-primary w-full flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed'
                >
                  {loading ? (
                    <>
                      <RefreshCw className='animate-spin' />
                      <span>Generating Magic...</span>
                    </>
                  ) : (
                    <>
                      <Sparkles />
                      <span>Generate Image</span>
                    </>
                  )}
                </button>

                {error && (
                  <div className='p-4 bg-red-50 border border-red-200 rounded-xl'>
                    <p className='text-red-700 text-sm'>{error}</p>
                  </div>
                )}
              </div>
            </div>

            {/* Features */}
            <div className='card'>
              <h3 className='font-semibold text-gray-800 mb-4'>
                ✨ How it works
              </h3>
              <div className='space-y-3'>
                <div className='flex items-center gap-3'>
                  <div className='w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center'>
                    <span className='text-primary-600 font-semibold text-sm'>
                      1
                    </span>
                  </div>
                  <span className='text-gray-600'>
                    Enter your image description
                  </span>
                </div>
                <div className='flex items-center gap-3'>
                  <div className='w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center'>
                    <span className='text-primary-600 font-semibold text-sm'>
                      2
                    </span>
                  </div>
                  <span className='text-gray-600'>AI enhances your prompt</span>
                </div>
                <div className='flex items-center gap-3'>
                  <div className='w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center'>
                    <span className='text-primary-600 font-semibold text-sm'>
                      3
                    </span>
                  </div>
                  <span className='text-gray-600'>
                    Get your optimized result
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Results Section */}
          <div className='space-y-6'>
            {result ? (
              <>
                {/* Generated Image */}
                <div className='card'>
                  <div className='flex items-center justify-between mb-4'>
                    <div className='flex items-center gap-2'>
                      <ImageIcon />
                      <h2 className='text-xl font-semibold text-gray-800'>
                        Generated Image
                      </h2>
                    </div>
                    <button
                      onClick={() =>
                        result.is_favorite
                          ? removeFromFavorites(result.image_id)
                          : addToFavorites(result.image_id)
                      }
                      className='p-2 hover:bg-gray-100 rounded-lg transition-colors'
                    >
                      <Heart filled={result.is_favorite} />
                    </button>
                  </div>

                  <div className='space-y-4'>
                    <div className='relative group'>
                      <img
                        src={result.image_url}
                        alt={result.improved_prompt}
                        className='w-full h-64 md:h-80 object-cover rounded-xl shadow-lg transition-transform duration-300 group-hover:scale-105'
                        style={{ maxWidth: '100%', height: 'auto' }} // Add this for better responsive handling
                      />
                      <div className='absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-10 rounded-xl transition-all duration-300 flex items-center justify-center'>
                        <button
                          onClick={() =>
                            window.open(result.image_url, '_blank')
                          }
                          className='opacity-0 group-hover:opacity-100 transition-opacity duration-300 btn-secondary flex items-center gap-2'
                        >
                          <Download />
                          <span>Download</span>
                        </button>
                      </div>
                    </div>

                    {/* AI Enhancement Badge */}
                    {result.ai_enhanced && (
                      <div className='flex items-center gap-2 text-sm text-primary-600 bg-primary-50 px-3 py-2 rounded-lg w-fit'>
                        <Sparkles />
                        <span>Enhanced with AI Magic</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Prompt Comparison */}
                <div className='card'>
                  <h3 className='font-semibold text-gray-800 mb-4'>
                    Prompt Evolution
                  </h3>
                  <div className='space-y-4'>
                    <div>
                      <label className='block text-sm font-medium text-gray-600 mb-2'>
                        Original Prompt
                      </label>
                      <div className='p-3 bg-gray-50 rounded-lg border border-gray-200'>
                        <p className='text-gray-700'>
                          {result.original_prompt}
                        </p>
                      </div>
                    </div>

                    <div>
                      <div className='flex items-center justify-between mb-2'>
                        <label className='block text-sm font-medium text-gray-600'>
                          Enhanced Prompt
                        </label>
                        <button
                          onClick={() =>
                            copyToClipboard(result.improved_prompt)
                          }
                          className='text-xs text-primary-600 hover:text-primary-700 font-medium'
                        >
                          Copy
                        </button>
                      </div>
                      <div className='p-3 bg-primary-50 rounded-lg border border-primary-200'>
                        <p className='text-gray-800 font-medium'>
                          {result.improved_prompt}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>

                <button
                  onClick={resetForm}
                  className='btn-secondary w-full flex items-center justify-center gap-2'
                >
                  <RefreshCw />
                  <span>Create Another</span>
                </button>
              </>
            ) : (
              /* Placeholder State */
              <div className='card h-full flex items-center justify-center min-h-96'>
                <div className='text-center text-gray-500'>
                  <ImageIcon className='w-16 h-16 mx-auto mb-4 text-gray-300' />
                  <p className='text-lg font-medium text-gray-400'>
                    Your creation awaits
                  </p>
                  <p className='text-sm mt-2'>
                    Enter a prompt to generate your first AI image
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className='text-center mt-12 pt-8 border-t border-gray-200'>
          <p className='text-gray-500 text-sm'>
            Powered by Google Gemini AI • Built with React & Tailwind CSS
          </p>
        </div>
      </div>
    </div>
  )
}

export default MainApp
