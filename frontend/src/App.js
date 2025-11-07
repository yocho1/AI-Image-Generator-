import React, { useState, useEffect } from 'react'
import Auth from './components/Auth'
import Profile from './components/Profile'
import MainApp from './components/MainApp'

function App() {
  const [user, setUser] = useState(null)
  const [currentView, setCurrentView] = useState('main')

  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem('token')
    const savedUser = localStorage.getItem('user')

    if (token && savedUser) {
      setUser(JSON.parse(savedUser))
    }
  }, [])

  const handleLogin = (userData) => {
    setUser(userData)
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    setUser(null)
    setCurrentView('main')
  }

  if (!user) {
    return <Auth onLogin={handleLogin} />
  }

  return (
    <div>
      {/* Navigation */}
      <nav className='bg-white shadow-sm border-b'>
        <div className='max-w-6xl mx-auto px-4'>
          <div className='flex justify-between items-center h-16'>
            <div className='flex items-center space-x-8'>
              <h1 className='text-xl font-bold bg-gradient-to-r from-primary-600 to-purple-600 bg-clip-text text-transparent'>
                AI Image Generator
              </h1>
              <div className='flex space-x-4'>
                <button
                  onClick={() => setCurrentView('main')}
                  className={`px-3 py-2 rounded-lg font-medium ${
                    currentView === 'main'
                      ? 'bg-primary-100 text-primary-700'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  Generate
                </button>
                <button
                  onClick={() => setCurrentView('profile')}
                  className={`px-3 py-2 rounded-lg font-medium ${
                    currentView === 'profile'
                      ? 'bg-primary-100 text-primary-700'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  My Images
                </button>
              </div>
            </div>
            <div className='flex items-center space-x-4'>
              <span className='text-gray-700'>Hello, {user.username}</span>
              <button onClick={handleLogout} className='btn-secondary text-sm'>
                Sign Out
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      {currentView === 'main' && <MainApp user={user} />}
      {currentView === 'profile' && (
        <Profile user={user} onLogout={handleLogout} />
      )}
    </div>
  )
}

export default App
