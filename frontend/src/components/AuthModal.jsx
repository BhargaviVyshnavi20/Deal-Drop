import { useEffect, useState } from 'react'
import { X } from 'lucide-react'
import { apiRequest } from '../api/client'
import { GoogleLogin } from '@react-oauth/google'

export default function AuthModal({
  mode,
  onClose,
  onSwitchMode,
  onAuthSuccess,
}) {
  const isSignIn = mode === 'signin'
  const isForgotPassword = mode === 'forgot-password'

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [forgotSuccess, setForgotSuccess] = useState(false)

  useEffect(() => {
    function handleKeyDown(event) {
      if (event.key === 'Escape') {
        onClose()
      }
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

  function openForgotPassword() {
    setError('')
    setForgotSuccess(false)

    // Tell the parent to show the forgot-password mode.
    onSwitchMode('forgot-password')
  }

  function backToSignIn() {
    setError('')
    setForgotSuccess(false)

    onSwitchMode('signin')
  }

  async function handleSubmit(event) {
    event.preventDefault()

    setError('')
    setLoading(true)

    const formData = new FormData(event.currentTarget)

    try {
      // =====================================================
      // FORGOT PASSWORD
      // =====================================================

      if (isForgotPassword) {
        await apiRequest('/auth/forgot-password', {
          method: 'POST',
          body: JSON.stringify({
            email: formData.get('email'),
          }),
        })

        setForgotSuccess(true)
        return
      }

      // =====================================================
      // SIGN IN
      // =====================================================

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

        return
      }

      // =====================================================
      // SIGN UP
      // =====================================================

      await apiRequest('/auth/signup', {
        method: 'POST',
        body: JSON.stringify({
          name: formData.get('name'),
          email: formData.get('email'),
          password: formData.get('password'),
        }),
      })

      // Switch back to sign in after successful signup.
      onSwitchMode('signin')

    } catch (err) {
      console.error('Authentication error:', err)

      if (err instanceof Error) {
        setError(err.message)
      } else {
        setError('Something went wrong. Please try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  // ===========================================================
  // GOOGLE LOGIN
  // ===========================================================

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
      console.error('Google sign-in error:', err)

      if (err instanceof Error) {
        setError(err.message)
      } else {
        setError(
          'Google sign-in failed. Please try again.'
        )
      }
    } finally {
      setLoading(false)
    }
  }

  // ===========================================================
  // FORGOT PASSWORD SUCCESS SCREEN
  // ===========================================================

  if (isForgotPassword && forgotSuccess) {
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

          <span
            className="modal-logo"
            aria-hidden="true"
          >
            <svg
              width="16"
              height="16"
              viewBox="0 0 16 16"
              fill="none"
            >
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

          <h2
            id="auth-modal-title"
            className="modal-title"
          >
            Check your email
          </h2>

          <p className="modal-subtitle">
            If an account exists with that email,
            we've sent a password reset link.
          </p>

          <div
            style={{
              marginTop: '24px',
              padding: '18px',
              borderRadius: '8px',
              backgroundColor: '#ecfdf5',
              color: '#166534',
              lineHeight: '1.5',
              fontSize: '14px',
            }}
          >
            Check your inbox for the DealDrop
            password reset email. The link will
            expire in 15 minutes.
          </div>

          <button
            type="button"
            className="btn btn-primary modal-submit"
            style={{ marginTop: '24px' }}
            onClick={backToSignIn}
          >
            Back to Sign In
          </button>
        </div>
      </div>
    )
  }

  // ===========================================================
  // MAIN MODAL
  // ===========================================================

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

        <span
          className="modal-logo"
          aria-hidden="true"
        >
          <svg
            width="16"
            height="16"
            viewBox="0 0 16 16"
            fill="none"
          >
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

        <h2
          id="auth-modal-title"
          className="modal-title"
        >
          {isForgotPassword
            ? 'Forgot your password?'
            : isSignIn
              ? 'Welcome back'
              : 'Create your account'}
        </h2>

        <p className="modal-subtitle">
          {isForgotPassword
            ? 'Enter your email and we will send you a password reset link.'
            : isSignIn
              ? 'Sign in to continue tracking prices.'
              : 'Start tracking prices and save money.'}
        </p>

        {/* =====================================================
            GOOGLE LOGIN
        ===================================================== */}

        {!isForgotPassword && (
          <>
            <GoogleLogin
              onSuccess={handleGoogleSuccess}
              onError={() => {
                setError(
                  'Google sign-in failed. Please try again.'
                )
              }}
            />

            <div className="modal-divider">
              <span>or</span>
            </div>
          </>
        )}

        {/* =====================================================
            FORM
        ===================================================== */}

        <form
          className="modal-form"
          onSubmit={handleSubmit}
        >
          {/* FULL NAME - SIGN UP ONLY */}
          {!isSignIn && !isForgotPassword && (
            <label className="field">
              <span className="field-label">
                Full Name
              </span>

              <input
                type="text"
                name="name"
                required
                minLength="2"
                maxLength="255"
                placeholder="Alex Johnson"
              />
            </label>
          )}

          {/* EMAIL */}
          <label className="field">
            <span className="field-label">
              Email
            </span>

            <input
              type="email"
              name="email"
              required
              placeholder="you@example.com"
            />
          </label>

          {/* PASSWORD - SIGN IN / SIGN UP ONLY */}
          {!isForgotPassword && (
            <label className="field">
              <span className="field-label">
                Password
              </span>

              <input
                type="password"
                name="password"
                required
                minLength="8"
                maxLength="100"
                placeholder="••••••••"
              />
            </label>
          )}

          {/* FORGOT PASSWORD LINK */}
          {isSignIn && (
            <button
              type="button"
              className="forgot-link"
              onClick={openForgotPassword}
              disabled={loading}
            >
              Forgot password?
            </button>
          )}

          {/* ERROR */}
          {error && (
            <p className="auth-error">
              {error}
            </p>
          )}

          {/* SUBMIT */}
          <button
            type="submit"
            className="btn btn-primary modal-submit"
            disabled={loading}
          >
            {loading
              ? 'Please wait...'
              : isForgotPassword
                ? 'Send Reset Link'
                : isSignIn
                  ? 'Sign In'
                  : 'Create Account'}
          </button>
        </form>

        {/* =====================================================
            BOTTOM NAVIGATION
        ===================================================== */}

        {isForgotPassword ? (
          <p className="modal-switch">
            Remember your password?{' '}

            <button
              type="button"
              className="modal-switch-link"
              onClick={backToSignIn}
              disabled={loading}
            >
              Sign In
            </button>
          </p>
        ) : (
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
              {isSignIn
                ? 'Sign Up'
                : 'Sign In'}
            </button>
          </p>
        )}
      </div>
    </div>
  )
}