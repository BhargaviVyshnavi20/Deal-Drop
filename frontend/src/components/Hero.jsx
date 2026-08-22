import { useState } from 'react'
import { Search, CheckCircle2, AlertCircle } from 'lucide-react'

const STORES = ['Amazon', 'Walmart', 'Flipkart', 'eBay']

export default function Hero({ user, onRequireAuth }) {
  const [url, setUrl] = useState('')
  const [status, setStatus] = useState(null) // { type: 'error' | 'info' | 'success', message: string }

  function handleTrack() {
    if (!url.trim()) {
      setStatus({ type: 'error', message: 'Please enter a product URL first.' })
      return
    }

    if (!user) {
      setStatus({ type: 'info', message: 'Sign up to start tracking this product.' })
      onRequireAuth()
      return
    }

    setStatus({ type: 'success', message: 'Product added to your tracking list.' })
    setUrl('')
  }

  function handleKeyDown(event) {
    if (event.key === 'Enter') handleTrack()
  }

  return (
    <section className="hero">
      <h1 className="hero-heading">
        <span className="hero-heading-dark">Never Miss a </span>
        <span className="hero-heading-accent">Price Drop</span>
      </h1>

      <p className="hero-subtext">
        Track prices from any e-commerce site. Get instant alerts when prices drop.
        <br />
        Save money effortlessly.
      </p>

      <div className="tracker">
        <div className="tracker-input-wrap">
          <Search size={18} className="tracker-icon" aria-hidden="true" />
          <input
            type="text"
            className="tracker-input"
            placeholder="Paste product URL (Amazon, Walmart, etc.)"
            aria-label="Product URL"
            value={url}
            onChange={(event) => setUrl(event.target.value)}
            onKeyDown={handleKeyDown}
          />
        </div>
        <button type="button" className="btn btn-primary tracker-btn" onClick={handleTrack}>
          Track Price
        </button>
      </div>

      {status && (
        <p className={`tracker-status tracker-status-${status.type}`} role="status">
          {status.type === 'success' ? (
            <CheckCircle2 size={16} />
          ) : status.type === 'error' ? (
            <AlertCircle size={16} />
          ) : null}
          {status.message}
        </p>
      )}

      <div className="stores">
        <p className="stores-label">Works with your favorite stores</p>
        <div className="stores-list">
          {STORES.map((store) => (
            <span key={store} className="store-name">
              {store}
            </span>
          ))}
        </div>
      </div>
    </section>
  )
}
