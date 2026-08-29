import { useState } from "react";
import "./TrackedProducts.css";


function TrackedProducts() {
  const [expandedProduct, setExpandedProduct] = useState(null);

  // Temporary sample data.
  // Later this will come from GET /products/
  const products = [
    {
      id: 1,
      name: "SanDisk Extreme Pro 256GB microSDXC Memory Card",
      currentPrice: 4995,
      lowestPrice: 4599,
      highestPrice: 5999,
      currency: "₹",
      image:
        "https://images.unsplash.com/photo-1618410320928-25228d811631?auto=format&fit=crop&w=300&q=80",
      productUrl: "#",
      history: [5999, 5800, 5600, 5400, 5200, 4995],
    },
    {
      id: 2,
      name: "Hooded Leather Effect Jacket",
      currentPrice: 3550,
      lowestPrice: 3200,
      highestPrice: 4200,
      currency: "₹",
      image:
        "https://images.unsplash.com/photo-1551028719-00167b16eac5?auto=format&fit=crop&w=300&q=80",
      productUrl: "#",
      history: [4200, 4100, 3900, 3800, 3700, 3550],
    },
  ];

  const calculateDropPercentage = (current, highest) => {
    return (((highest - current) / highest) * 100).toFixed(1);
  };

  const getPosition = (value, min, max) => {
    if (max === min) return 50;

    return ((value - min) / (max - min)) * 100;
  };

  return (
    <section className="tracked-products-section">
      <div className="tracked-products-header">
        <div>
          <p className="section-label">YOUR SAVINGS</p>

          <h2>Your Tracked Products</h2>

          <p className="section-subtitle">
            Monitor prices and catch the best deals.
          </p>
        </div>

        <div className="product-count">
          {products.length} Products
        </div>
      </div>

      <div className="products-grid">
        {products.map((product) => {
          const isExpanded = expandedProduct === product.id;

          const dropPercentage = calculateDropPercentage(
            product.currentPrice,
            product.highestPrice
          );

          const priceRange =
            product.highestPrice - product.lowestPrice;

          const currentPosition = getPosition(
            product.currentPrice,
            product.lowestPrice,
            product.highestPrice
          );

          return (
            <article
              className={`product-card ${
                isExpanded ? "product-card-expanded" : ""
              }`}
              key={product.id}
            >
              {/* Product information */}

              <div className="product-top">
                <div className="product-image-container">
                  <img
                    src={product.image}
                    alt={product.name}
                    className="product-image"
                  />
                </div>

                <div className="product-main-info">
                  <h3>{product.name}</h3>

                  <div className="current-price-row">
                    <span className="current-price">
                      {product.currency}
                      {product.currentPrice.toLocaleString("en-IN")}
                    </span>

                    <span className="tracking-badge">
                      ● Tracking
                    </span>
                  </div>

                  <div className="price-drop">
                    ↓ {dropPercentage}% below highest price
                  </div>
                </div>
              </div>

              {/* Price statistics */}

              <div className="price-stats">
                <div className="stat-box">
                  <span className="stat-label">
                    LOWEST
                  </span>

                  <strong>
                    {product.currency}
                    {product.lowestPrice.toLocaleString("en-IN")}
                  </strong>
                </div>

                <div className="stat-box">
                  <span className="stat-label">
                    CURRENT
                  </span>

                  <strong className="current-stat">
                    {product.currency}
                    {product.currentPrice.toLocaleString("en-IN")}
                  </strong>
                </div>

                <div className="stat-box">
                  <span className="stat-label">
                    HIGHEST
                  </span>

                  <strong>
                    {product.currency}
                    {product.highestPrice.toLocaleString("en-IN")}
                  </strong>
                </div>
              </div>

              {/* Price range */}

              <div className="price-range-section">
                <div className="range-labels">
                  <span>Lowest price</span>

                  <span>
                    Range: {product.currency}
                    {priceRange.toLocaleString("en-IN")}
                  </span>

                  <span>Highest price</span>
                </div>

                <div className="price-range-bar">
                  <div
                    className="current-price-marker"
                    style={{
                      left: `${currentPosition}%`,
                    }}
                  >
                    <span className="marker-tooltip">
                      Current
                    </span>
                  </div>
                </div>
              </div>

              {/* Actions */}

              <div className="product-actions">
                <button
                  className="chart-button"
                  onClick={() =>
                    setExpandedProduct(
                      isExpanded ? null : product.id
                    )
                  }
                >
                  {isExpanded
                    ? "⌃ Hide Chart"
                    : "⌄ Show Chart"}
                </button>

                <a
                  href={product.productUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="view-product-button"
                >
                  ↗ View Product
                </a>

                <button className="remove-button">
                  🗑 Remove
                </button>
              </div>

              {/* Expandable chart */}

              {isExpanded && (
                <div className="chart-container">
                  <div className="chart-header">
                    <div>
                      <h4>Price History</h4>

                      <p>
                        Track how this product's price
                        has changed over time.
                      </p>
                    </div>

                    <span className="chart-badge">
                      {dropPercentage}% Drop
                    </span>
                  </div>

                  <div className="chart-area">
                    <svg
                      viewBox="0 0 600 220"
                      className="price-chart"
                      preserveAspectRatio="none"
                    >
                      {/* Grid lines */}

                      <line
                        x1="0"
                        y1="40"
                        x2="600"
                        y2="40"
                        className="grid-line"
                      />

                      <line
                        x1="0"
                        y1="100"
                        x2="600"
                        y2="100"
                        className="grid-line"
                      />

                      <line
                        x1="0"
                        y1="160"
                        x2="600"
                        y2="160"
                        className="grid-line"
                      />

                      {/* Chart line */}

                      <polyline
                        points="0,30 120,45 240,75 360,95 480,125 600,160"
                        className="chart-line"
                      />

                      {/* Data points */}

                      <circle
                        cx="0"
                        cy="30"
                        r="6"
                        className="chart-point"
                      />

                      <circle
                        cx="120"
                        cy="45"
                        r="6"
                        className="chart-point"
                      />

                      <circle
                        cx="240"
                        cy="75"
                        r="6"
                        className="chart-point"
                      />

                      <circle
                        cx="360"
                        cy="95"
                        r="6"
                        className="chart-point"
                      />

                      <circle
                        cx="480"
                        cy="125"
                        r="6"
                        className="chart-point"
                      />

                      <circle
                        cx="600"
                        cy="160"
                        r="6"
                        className="chart-point"
                      />
                    </svg>
                  </div>

                  <div className="chart-footer">
                    <span>Older</span>

                    <span>Latest price</span>
                  </div>
                </div>
              )}
            </article>
          );
        })}
      </div>
    </section>
  );
}


export default TrackedProducts;