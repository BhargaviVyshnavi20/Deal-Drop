import { Moon, Sun } from 'lucide-react'
import ProfileDropdown from './ProfileDropdown.jsx'

export default function Header({ theme, onToggleTheme, user, onOpenSignIn, onOpenSignUp, onSignOut }) {
  return (
    <header className="header">
      <div className="header-inner">
        <div className="logo">
          <span className="logo-icon" aria-hidden="true">
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
          <span className="logo-text">dealdrop</span>
        </div>

        <div className="header-actions">
          <button
            type="button"
            className="icon-btn theme-toggle"
            onClick={onToggleTheme}
            aria-label={theme === 'light' ? 'Switch to dark mode' : 'Switch to light mode'}
          >
            {theme === 'light' ? <Moon size={18} /> : <Sun size={18} />}
          </button>

          {user ? (
            <ProfileDropdown user={user} onSignOut={onSignOut} />
          ) : (
            <>
              <button type="button" className="btn btn-ghost" onClick={onOpenSignIn}>
                Sign In
              </button>
              <button type="button" className="btn btn-primary" onClick={onOpenSignUp}>
                Sign Up
              </button>
            </>
          )}
        </div>
      </div>
    </header>
  )
}
