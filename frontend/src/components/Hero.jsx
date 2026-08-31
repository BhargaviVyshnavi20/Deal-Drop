import { useState } from "react";
import {
  Search,
  CheckCircle2,
  AlertCircle,
  Loader2,
} from "lucide-react";

const STORES = ["Amazon", "Walmart", "Flipkart", "eBay", 'etc..'];

export default function Hero({
  user,
  onRequireAuth,
  onProductTracked,
}) {
  const [url, setUrl] = useState("");

  const [status, setStatus] = useState(null);

  const [isTracking, setIsTracking] = useState(false);

  async function handleTrack() {
    // Check if URL is entered
    if (!url.trim()) {
      setStatus({
        type: "error",
        message: "Please enter a product URL first.",
      });
      return;
    }

    // Check authentication
    if (!user) {
      setStatus({
        type: "info",
        message: "Sign up to start tracking this product.",
      });

      onRequireAuth();
      return;
    }

    // Get JWT token
    const token = localStorage.getItem("access_token");

    if (!token) {
      setStatus({
        type: "error",
        message: "Authentication token not found. Please sign in again.",
      });
      return;
    }

    try {
      setIsTracking(true);

      setStatus({
        type: "info",
        message: "Fetching product details...",
      });

      const response = await fetch(
        "https://deal-drop-jp5q.onrender.com/products/track",
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",

            Authorization: `Bearer ${token}`,
          },

          body: JSON.stringify({
            url: url.trim(),
          }),
        }
      );

      const data = await response.json();

      // Handle backend errors
      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to track product."
        );
      }

      // Success
      setStatus({
        type: "success",
        message: "Product added to your tracking list successfully!",
      });

      setUrl("");

      // Tell parent component to refresh products
      if (onProductTracked) {
        onProductTracked(data.product);
      }

    } catch (error) {
      console.error("Error tracking product:", error);

      setStatus({
        type: "error",
        message:
          error.message ||
          "Something went wrong while tracking the product.",
      });

    } finally {
      setIsTracking(false);
    }
  }

  function handleKeyDown(event) {
    if (event.key === "Enter" && !isTracking) {
      handleTrack();
    }
  }

  return (
    <section className="hero">

      <h1 className="hero-heading">
        <span className="hero-heading-dark">
          Never Miss a{" "}
        </span>

        <span className="hero-heading-accent">
          Price Drop
        </span>
      </h1>

      <p className="hero-subtext">
        Track prices from any e-commerce site. Get instant alerts when prices drop.
        <br />
        Save money effortlessly.
      </p>

      <div className="tracker">

        <div className="tracker-input-wrap">
          <Search
            size={18}
            className="tracker-icon"
            aria-hidden="true"
          />

          <input
            type="text"
            className="tracker-input"
            placeholder="Paste product URL (Amazon, Walmart, etc.)"
            aria-label="Product URL"
            value={url}
            onChange={(event) =>
              setUrl(event.target.value)
            }
            onKeyDown={handleKeyDown}
            disabled={isTracking}
          />
        </div>

        <button
          type="button"
          className="btn btn-primary tracker-btn"
          onClick={handleTrack}
          disabled={isTracking}
        >
          {isTracking ? (
            <>
              <Loader2
                size={18}
                className="animate-spin"
              />
              Tracking...
            </>
          ) : (
            "Track Price"
          )}
        </button>

      </div>

      {status && (
        <p
          className={`tracker-status tracker-status-${status.type}`}
          role="status"
        >
          {status.type === "success" ? (
            <CheckCircle2 size={16} />

          ) : status.type === "error" ? (
            <AlertCircle size={16} />

          ) : null}

          {status.message}
        </p>
      )}

      <div className="stores">

        <p className="stores-label">
          Works with your favorite stores
        </p>

        <div className="stores-list">
          {STORES.map((store) => (
            <span
              key={store}
              className="store-name"
            >
              {store}
            </span>
          ))}
        </div>

      </div>

    </section>
  );
}
