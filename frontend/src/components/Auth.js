import React, { useState } from 'react'

const Auth = ({ onLogin, onSwitchMode }) => {
  const [isLogin, setIsLogin] = useState(true)
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const endpoint = isLogin ? '/api/login' : '/api/register'
      const response = await fetch(`http://127.0.0.1:5002${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      })

      const data = await response.json()

      if (response.ok) {
        localStorage.setItem('token', data.access_token)
        localStorage.setItem('user', JSON.stringify(data.user))
        onLogin(data.user)
      } else {
        setError(data.error || 'Authentication failed')
      }
    } catch (err) {
      setError('Network error. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    })
  }

  const switchMode = () => {
    setIsLogin(!isLogin)
    setError('')
    setFormData({ username: '', email: '', password: '' })
  }

  return (
    <div className='min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 flex items-center justify-center py-8 px-4'>
      <div className='max-w-md w-full'>
        <div className='card'>
          <div className='text-center mb-6'>
            <h2 className='text-3xl font-bold bg-gradient-to-r from-primary-600 to-purple-600 bg-clip-text text-transparent'>
              {isLogin ? 'Welcome Back' : 'Create Account'}
            </h2>
            <p className='text-gray-600 mt-2'>
              {isLogin
                ? 'Sign in to your account'
                : 'Join us to start generating images'}
            </p>
          </div>

          <form onSubmit={handleSubmit} className='space-y-4'>
            {!isLogin && (
              <div>
                <label className='block text-sm font-medium text-gray-700 mb-2'>
                  Username
                </label>
                <input
                  type='text'
                  name='username'
                  value={formData.username}
                  onChange={handleChange}
                  className='input-field'
                  placeholder='Enter your username'
                  required
                />
              </div>
            )}

            <div>
              <label className='block text-sm font-medium text-gray-700 mb-2'>
                Email
              </label>
              <input
                type='email'
                name='email'
                value={formData.email}
                onChange={handleChange}
                className='input-field'
                placeholder='Enter your email'
                required
              />
            </div>

            <div>
              <label className='block text-sm font-medium text-gray-700 mb-2'>
                Password
              </label>
              <input
                type='password'
                name='password'
                value={formData.password}
                onChange={handleChange}
                className='input-field'
                placeholder='Enter your password'
                required
                minLength='6'
              />
            </div>

            {error && (
              <div className='p-3 bg-red-50 border border-red-200 rounded-lg'>
                <p className='text-red-700 text-sm'>{error}</p>
              </div>
            )}

            <button
              type='submit'
              disabled={loading}
              className='btn-primary w-full flex items-center justify-center gap-2 disabled:opacity-50'
            >
              {loading
                ? 'Please wait...'
                : isLogin
                ? 'Sign In'
                : 'Create Account'}
            </button>
          </form>

          <div className='mt-6 text-center'>
            <button
              onClick={switchMode}
              className='text-primary-600 hover:text-primary-700 font-medium'
            >
              {isLogin
                ? "Don't have an account? Sign up"
                : 'Already have an account? Sign in'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Auth
