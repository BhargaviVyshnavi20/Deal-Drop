import { useEffect, useRef, useState } from 'react'
import { ChevronDown, LogOut, User } from 'lucide-react'

export default function ProfileDropdown({ user, onSignOut }) {
  const [open, setOpen] = useState(false)
  const rootRef = useRef(null)

  useEffect(() => {
    function handleClickOutside(event) {
      if (rootRef.current && !rootRef.current.contains(event.target)) {
        setOpen(false)
      }
    }
    function handleKeyDown(event) {
      if (event.key === 'Escape') setOpen(false)
    }
    document.addEventListener('mousedown', handleClickOutside)
    document.addEventListener('keydown', handleKeyDown)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
      document.removeEventListener('keydown', handleKeyDown)
    }
  }, [])

  const initial = user.name?.charAt(0)?.toUpperCase() || '?'

  return (
    <div className="profile" ref={rootRef}>
      <button
        type="button"
        className="profile-trigger"
        onClick={() => setOpen((prev) => !prev)}
        aria-haspopup="true"
        aria-expanded={open}
      >
        <span className="avatar">{initial}</span>
        <span className="profile-name">{user.name}</span>
        <ChevronDown size={16} className={`chevron ${open ? 'chevron-open' : ''}`} />
      </button>

      {open && (
        <div className="profile-dropdown" role="menu">
          <div className="profile-dropdown-header">
            <span className="avatar avatar-lg">{initial}</span>
            <div>
              <p className="profile-dropdown-name">{user.name}</p>
              <p className="profile-dropdown-email">{user.email}</p>
            </div>
          </div>
          <div className="profile-dropdown-divider" />
          <button type="button" className="profile-dropdown-item" role="menuitem">
            <User size={16} />
            Profile
          </button>
          <button
            type="button"
            className="profile-dropdown-item profile-dropdown-item-danger"
            role="menuitem"
            onClick={() => {
              setOpen(false)
              onSignOut()
            }}
          >
            <LogOut size={16} />
            Sign Out
          </button>
        </div>
      )}
    </div>
  )
}
