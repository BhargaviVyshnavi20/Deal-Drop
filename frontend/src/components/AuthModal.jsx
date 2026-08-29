import { useEffect, useState } from 'react'
import { X } from 'lucide-react'
import { apiRequest } from '../api/client'

import { GoogleLogin } from '@react-oauth/google'

const GOOGLE_ICON = (
  <svg width="18" height="18" viewBox="0 0 18 18" aria-hidden="true">
    <path
      fill="#4285F4"
      d="M17.64 9.2c0-.64-.06-1.25-.16-1.84H9v3.48h4.84a4.14 4.14 0 0 1-1.8 2.72v2.26h2.9c1.7-1.57 2.7-3.87 2.7-6.62z"
    />
    <path
      fill="#34A853"
      d="M9 18c2.43 0 4.47-.8 5.96-2.18l-2.9-2.26c-.8.54-1.84.86-3.06.86-2.35 0-4.34-1.59-5.05-3.72H.95v2.33A9 9 0 0 0 9 18z"
    />
    <path
      fill="#FBBC05"
      d="M3.95 10.7A5.4 5.4 0 0 1 3.67 9c0-.59.1-1.17.28-1.7V4.97H.95A9 9 0 0 0 0 9c0 1.45.35 2.83.95 4.03l3-2.33z"
    />
    <path
      fill="#EA4335"
      d="M9 3.58c1.32 0 2.51.46 3.44 1.35l2.58-2.58C13.46.89 11.43 0 9 0A9 9 0 0 0 .95 4.97l3 2.33C4.66 5.17 6.65 3.58 9 3.58z"
    />
  </svg>
)

export default function AuthModal({
  mode,
  onClose,
  onSwitchMode,
  onAuthSuccess,
}) {
  const isSignIn = mode === 'signin'

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    function handleKeyDown(event) {
      if (event.key === 'Escape') onClose()
    }

    document.addEventListener('keydown', handleKeyDown)
    document.body.style.overflow = 'hidden'

    return () => {
      document.removeEventListener('keydown', handleKeyDown)
      document.body.style.overflow = ''
    }
  }, [onClose])


  function handleOverlayClick(event) {
    if (event.target === event.currentTarget) {
      onClose()
    }
  }


  async function handleSubmit(event) {
    event.preventDefault()

    setError('')
    setLoading(true)

    const formData = new FormData(event.currentTarget)

    try {
      if (isSignIn) {
        const data = await apiRequest('/auth/login', {
          method: 'POST',
          body: JSON.stringify({
            email: formData.get('email'),
            password: formData.get('password'),
          }),
        })

        localStorage.setItem(
          'access_token',
          data.access_token
        )

        const userData = await apiRequest('/auth/me')

        onAuthSuccess(userData)
      } else {
        // SIGNUP
        await apiRequest('/auth/signup', {
          method: 'POST',
          body: JSON.stringify({
            name: formData.get('name'),
            email: formData.get('email'),
            password: formData.get('password'),
          }),
        })

        // Switch to login after successful signup
        onSwitchMode()
      }

    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }


    async function handleGoogleSuccess(credentialResponse) {
    setError('')
    setLoading(true)

    try {
      const data = await apiRequest('/auth/google', {
        method: 'POST',
        body: JSON.stringify({
          token: credentialResponse.credential,
        }),
      })

      localStorage.setItem(
        'access_token',
        data.access_token
      )

      const userData = await apiRequest('/auth/me')

      onAuthSuccess(userData)

    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }


  return (
    <div
      className="modal-overlay"
      onMouseDown={handleOverlayClick}
    >
      <div
        className="modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="auth-modal-title"
      >
        <button
          type="button"
          className="modal-close"
          onClick={onClose}
          aria-label="Close"
        >
          <X size={18} />
        </button>

        <span className="modal-logo" aria-hidden="true">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <rect
              x="8"
              y="1"
              width="9.9"
              height="9.9"
              rx="2"
              transform="rotate(45 8 1)"
              fill="currentColor"
            />
          </svg>
        </span>

        <h2 id="auth-modal-title" className="modal-title">
          {isSignIn ? 'Welcome back' : 'Create your account'}
        </h2>

        <p className="modal-subtitle">
          {isSignIn
            ? 'Sign in to continue tracking prices.'
            : 'Start tracking prices and save money.'}
        </p>

        {/* We'll connect Google next */}
          <GoogleLogin
            onSuccess={handleGoogleSuccess}
            onError={() => {
              setError('Google sign-in failed. Please try again.')
            }}
          />

        <div className="modal-divider">
          <span>or</span>
        </div>

        <form className="modal-form" onSubmit={handleSubmit}>
          {!isSignIn && (
            <label className="field">
              <span className="field-label">Full Name</span>
              <input
                type="text"
                name="name"
                required
                minLength="2"
                placeholder="Alex Johnson"
              />
            </label>
          )}

          <label className="field">
            <span className="field-label">Email</span>
            <input
              type="email"
              name="email"
              required
              placeholder="you@example.com"
            />
          </label>

          <label className="field">
            <span className="field-label">Password</span>
            <input
              type="password"
              name="password"
              required
              minLength="8"
              placeholder="••••••••"
            />
          </label>

          {isSignIn && (
            <a href="#forgot" className="forgot-link">
              Forgot password?
            </a>
          )}

          {error && (
            <p className="auth-error">
              {error}
            </p>
          )}

          <button
            type="submit"
            className="btn btn-primary modal-submit"
            disabled={loading}
          >
            {loading
              ? 'Please wait...'
              : isSignIn
                ? 'Sign In'
                : 'Create Account'}
          </button>
        </form>

        <p className="modal-switch">
          {isSignIn
            ? "Don't have an account? "
            : 'Already have an account? '}

          <button
            type="button"
            className="modal-switch-link"
            onClick={onSwitchMode}
            disabled={loading}
          >
            {isSignIn ? 'Sign Up' : 'Sign In'}
          </button>
        </p>
      </div>
    </div>
  )
}