import { useEffect, useState } from 'react'

import Header from './components/Header.jsx'
import Hero from './components/Hero.jsx'
import AuthModal from './components/AuthModal.jsx'
import FeatureSection from './components/FeatureSection.jsx'
import Footer from './components/Footer.jsx'
import TrackedProducts from './components/TrackedProducts.jsx'



function getInitialTheme() {
  if (typeof window === 'undefined') return 'light'

  const stored = window.localStorage.getItem('dealdrop-theme')

  if (stored === 'light' || stored === 'dark') {
    return stored
  }

  return window.matchMedia?.('(prefers-color-scheme: dark)').matches
    ? 'dark'
    : 'light'
}

export default function App() {
  const [theme, setTheme] = useState(getInitialTheme)
  const [user, setUser] = useState(null)
  const [authModal, setAuthModal] = useState(null)

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)

    window.localStorage.setItem(
      'dealdrop-theme',
      theme
    )
  }, [theme])

  function toggleTheme() {
    setTheme((prev) =>
      prev === 'light' ? 'dark' : 'light'
    )
  }

  function handleAuthSuccess(userData) {
    setUser(userData)
    setAuthModal(null)
  }

  function handleSignOut() {
    localStorage.removeItem('access_token')
    setUser(null)
  }

  return (
    <div className="app">
      <Header
        theme={theme}
        onToggleTheme={toggleTheme}
        user={user}
        onOpenSignIn={() => setAuthModal('signin')}
        onOpenSignUp={() => setAuthModal('signup')}
        onSignOut={handleSignOut}
      />

      <main>
        <Hero
          user={user}
          onRequireAuth={() => setAuthModal('signup')}
        />

        {user ? (
          <TrackedProducts />
        ) : (
          <FeatureSection
            onOpenSignUp={() => setAuthModal('signup')}
          />
        )}
      </main>

      <Footer />

      {authModal && (
        <AuthModal
          mode={authModal}
          onClose={() => setAuthModal(null)}
          onSwitchMode={() =>
            setAuthModal(
              authModal === 'signin'
                ? 'signup'
                : 'signin'
            )
          }
          onAuthSuccess={handleAuthSuccess}
        />
      )}
    </div>
  )
}