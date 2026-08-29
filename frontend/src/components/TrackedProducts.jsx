import { useEffect, useState } from "react";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";

import {
  TrendingUp,
  TrendingDown,
  Minus,
} from "lucide-react";

import { apiRequest } from "../api/client";

import "./TrackedProducts.css";

function TrackedProducts({ refreshTrigger }) {
  const [expandedProduct, setExpandedProduct] = useState(null);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Price history states
  const [priceHistory, setPriceHistory] = useState({});
  const [historyLoading, setHistoryLoading] = useState({});
  const [historyError, setHistoryError] = useState({});

  // Remove modal states
  const [productToRemove, setProductToRemove] = useState(null);
  const [removingProductId, setRemovingProductId] = useState(null);

  // =========================================================
  // FORMAT CURRENCY
  // =========================================================

  const formatCurrency = (price, currencyCode) => {
    if (price === null || price === undefined) {
      return "—";
    }

    const currencyMap = {
      "Rs.": "INR",
      Rs: "INR",
      "₹": "INR",
      INR: "INR",
      "$": "USD",
      USD: "USD",
      "€": "EUR",
      EUR: "EUR",
      "£": "GBP",
      GBP: "GBP",
    };

    const normalizedCurrency =
      currencyMap[currencyCode] || "INR";

    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: normalizedCurrency,
      maximumFractionDigits: 2,
    }).format(Number(price));
  };

  // =========================================================
  // FETCH AND FORMAT ONE PRODUCT'S PRICE HISTORY
  // =========================================================

  async function getProductHistory(productId) {
    const data = await apiRequest(
      `/products/${productId}/price-history`
    );

    return (data.priceHistory || [])
      .map((item) => ({
        id: item.id,
        price: Number(item.price),
        recordedAt: item.recordedAt,

        date: new Date(
          item.recordedAt
        ).toLocaleDateString("en-IN", {
          day: "2-digit",
          month: "short",
        }),

        fullDate: new Date(
          item.recordedAt
        ).toLocaleString("en-IN"),
      }))
      .sort(
        (a, b) =>
          new Date(a.recordedAt) -
          new Date(b.recordedAt)
      );
  }

  // =========================================================
  // CALCULATE PRICE CHANGE
  // =========================================================

  function getPriceChange(history) {
    // Need at least two records
    if (!history || history.length < 2) {
      return {
        type: "neutral",
        percentage: 0,
        difference: 0,
      };
    }

    const previousPrice = Number(
      history[history.length - 2].price
    );

    const latestPrice = Number(
      history[history.length - 1].price
    );

    // Prevent invalid calculations
    if (
      !Number.isFinite(previousPrice) ||
      !Number.isFinite(latestPrice) ||
      previousPrice <= 0
    ) {
      return {
        type: "neutral",
        percentage: 0,
        difference: 0,
      };
    }

    const difference =
      latestPrice - previousPrice;

    // Floating point safety
    if (Math.abs(difference) < 0.01) {
      return {
        type: "neutral",
        percentage: 0,
        difference: 0,
      };
    }

    const percentage =
      Math.abs(
        (difference / previousPrice) * 100
      );

    // Price decreased
    if (difference < 0) {
      return {
        type: "decrease",
        percentage,
        difference: Math.abs(difference),
      };
    }

    // Price increased
    return {
      type: "increase",
      percentage,
      difference,
    };
  }

  // =========================================================
  // FETCH PRODUCTS + ALL PRICE HISTORIES
  // =========================================================

  useEffect(() => {
    let isMounted = true;

    async function fetchProductsAndHistory() {
      try {
        if (isMounted) {
          setLoading(true);
          setError("");
        }

        // Step 1: Fetch products
        const data = await apiRequest("/products/");

        const fetchedProducts =
          data.products || [];

        if (!isMounted) return;

        setProducts(fetchedProducts);

        // No products
        if (fetchedProducts.length === 0) {
          setPriceHistory({});
          setHistoryLoading({});
          setHistoryError({});
          return;
        }

        // Step 2: Mark all histories as loading
        const loadingState = {};

        fetchedProducts.forEach((product) => {
          loadingState[product.id] = true;
        });

        setHistoryLoading(loadingState);
        setHistoryError({});

        // Step 3: Fetch all histories in parallel
        const historyResults =
          await Promise.allSettled(
            fetchedProducts.map((product) =>
              getProductHistory(product.id)
            )
          );

        if (!isMounted) return;

        const loadedHistory = {};
        const loadedErrors = {};

        historyResults.forEach(
          (result, index) => {
            const productId =
              fetchedProducts[index].id;

            if (result.status === "fulfilled") {
              loadedHistory[productId] =
                result.value;
            } else {
              console.error(
                `Failed to load history for product ${productId}:`,
                result.reason
              );

              loadedHistory[productId] = [];

              loadedErrors[productId] =
                "Could not load price history.";
            }
          }
        );

        if (isMounted) {
          setPriceHistory(loadedHistory);
          setHistoryError(loadedErrors);
        }
      } catch (err) {
        console.error(
          "Error refreshing products:",
          err
        );

        if (isMounted) {
          setError(
            err.message ||
              "Failed to load tracked products."
          );
        }
      } finally {
        if (isMounted) {
          setLoading(false);
          setHistoryLoading({});
        }
      }
    }

    // Fetch immediately
    fetchProductsAndHistory();

    // Refresh frontend data every 5 minutes
    // This does NOT trigger a Firecrawl price check.
    const refreshInterval = setInterval(
      fetchProductsAndHistory,
      5 * 60 * 1000
    );

    // Cleanup
    return () => {
      isMounted = false;
      clearInterval(refreshInterval);
    };
  }, [refreshTrigger]);

  // =========================================================
  // SHOW / HIDE CHART
  // =========================================================

  function handleToggleChart(productId) {
    if (expandedProduct === productId) {
      setExpandedProduct(null);
    } else {
      setExpandedProduct(productId);
    }
  }

  // =========================================================
  // REMOVE PRODUCT
  // =========================================================

  async function handleRemove() {
    if (!productToRemove) return;

    try {
      setRemovingProductId(
        productToRemove.id
      );

      setError("");

      await apiRequest(
        `/products/${productToRemove.id}`,
        {
          method: "DELETE",
        }
      );

      // Remove product from UI
      setProducts((currentProducts) =>
        currentProducts.filter(
          (product) =>
            product.id !== productToRemove.id
        )
      );

      // Remove price history
      setPriceHistory((previous) => {
        const updated = { ...previous };

        delete updated[productToRemove.id];

        return updated;
      });

      // Remove loading state
      setHistoryLoading((previous) => {
        const updated = { ...previous };

        delete updated[productToRemove.id];

        return updated;
      });

      // Remove error state
      setHistoryError((previous) => {
        const updated = { ...previous };

        delete updated[productToRemove.id];

        return updated;
      });

      // Close chart if removed product was expanded
      if (
        expandedProduct ===
        productToRemove.id
      ) {
        setExpandedProduct(null);
      }

      setProductToRemove(null);
    } catch (err) {
      console.error(
        "Error removing product:",
        err
      );

      setError(
        err.message ||
          "Failed to remove the product."
      );

      setProductToRemove(null);
    } finally {
      setRemovingProductId(null);
    }
  }

  // =========================================================
  // LOADING STATE
  // =========================================================

  if (loading && products.length === 0) {
    return (
      <section className="tracked-products-section">
        <p className="products-loading">
          Loading your tracked products...
        </p>
      </section>
    );
  }

  // =========================================================
  // ERROR STATE
  // =========================================================

  if (error && products.length === 0) {
    return (
      <section className="tracked-products-section">
        <p className="products-error">
          {error}
        </p>
      </section>
    );
  }

  // =========================================================
  // MAIN COMPONENT
  // =========================================================

  return (
    <>
      <section className="tracked-products-section">

        {/* HEADER */}
        <div className="tracked-products-header">
          <div>
            <p className="section-label">
              YOUR SAVINGS
            </p>

            <h2>
              Your Tracked Products
            </h2>

            <p className="section-subtitle">
              Monitor prices and catch the best deals.
            </p>
          </div>

          <div className="product-count">
            {products.length}{" "}
            {products.length === 1
              ? "Product"
              : "Products"}
          </div>
        </div>

        {/* ERROR MESSAGE */}
        {error && (
          <p className="products-error">
            {error}
          </p>
        )}

        {/* EMPTY STATE */}
        {products.length === 0 ? (
          <div className="empty-products">
            <h3>
              No tracked products yet
            </h3>

            <p>
              Paste a product URL above to start
              tracking its price.
            </p>
          </div>
        ) : (
          <div className="products-grid">

            {products.map((product) => {
              const isExpanded =
                expandedProduct === product.id;

              const chartData =
                priceHistory[product.id] || [];

              // Calculate price change
              const priceChange =
                getPriceChange(chartData);

              // Get all prices
              const prices = chartData.map(
                (item) => item.price
              );

              // Lowest price
              const lowestPrice =
                prices.length > 0
                  ? Math.min(...prices)
                  : null;

              // Highest price
              const highestPrice =
                prices.length > 0
                  ? Math.max(...prices)
                  : null;

              return (
                <article
                  className={`product-card ${
                    isExpanded
                      ? "product-card-expanded"
                      : ""
                  }`}
                  key={product.id}
                >

                  {/* PRODUCT INFORMATION */}
                  <div className="product-top">

                    {/* PRODUCT IMAGE */}
                    <div className="product-image-container">
                      {product.productImageUrl ? (
                        <img
                          src={
                            product.productImageUrl
                          }
                          alt={
                            product.productName
                          }
                          className="product-image"
                        />
                      ) : (
                        <div className="product-image-placeholder">
                          No Image
                        </div>
                      )}
                    </div>

                    {/* PRODUCT DETAILS */}
                    <div className="product-main-info">
                      <h3>
                        {product.productName}
                      </h3>

                      <div className="current-price-row">
                        <span className="current-price">
                          {formatCurrency(
                            product.currentPrice,
                            product.currencyCode
                          )}
                        </span>

                        <span className="tracking-badge">
                          ● Tracking
                        </span>
                      </div>

                      {/* PRICE CHANGE INDICATOR */}
                      <div
                        className={`price-change price-change-${priceChange.type}`}
                      >

                        {/* PRICE INCREASE */}
                        {priceChange.type ===
                          "increase" && (
                          <>
                            <TrendingUp size={16} />

                            <span>
                              {priceChange.percentage.toFixed(
                                1
                              )}
                              % increase
                            </span>
                          </>
                        )}

                        {/* PRICE DECREASE */}
                        {priceChange.type ===
                          "decrease" && (
                          <>
                            <TrendingDown size={16} />

                            <span>
                              {priceChange.percentage.toFixed(
                                1
                              )}
                              % decrease
                            </span>
                          </>
                        )}

                        {/* NO CHANGE */}
                        {priceChange.type ===
                          "neutral" && (
                          <>
                            <Minus size={16} />

                            <span>
                              No price change
                            </span>
                          </>
                        )}

                      </div>
                    </div>

                  </div>

                  {/* PRICE STATISTICS */}
                  <div className="price-stats">

                    {/* CURRENT */}
                    <div className="stat-box">
                      <span className="stat-label">
                        CURRENT
                      </span>

                      <strong className="current-stat">
                        {formatCurrency(
                          product.currentPrice,
                          product.currencyCode
                        )}
                      </strong>
                    </div>

                    {/* LOWEST */}
                    <div className="stat-box">
                      <span className="stat-label">
                        LOWEST
                      </span>

                      <strong className="lowest-stat">
                        {historyLoading[product.id]
                          ? "Loading..."
                          : formatCurrency(
                              lowestPrice,
                              product.currencyCode
                            )}
                      </strong>
                    </div>

                    {/* HIGHEST */}
                    <div className="stat-box">
                      <span className="stat-label">
                        HIGHEST
                      </span>

                      <strong className="highest-stat">
                        {historyLoading[product.id]
                          ? "Loading..."
                          : formatCurrency(
                              highestPrice,
                              product.currencyCode
                            )}
                      </strong>
                    </div>

                  </div>

                  {/* ACTION BUTTONS */}
                  <div className="product-actions">

                    {/* SHOW / HIDE CHART */}
                    <button
                      type="button"
                      className="chart-button"
                      onClick={() =>
                        handleToggleChart(
                          product.id
                        )
                      }
                    >
                      {isExpanded
                        ? "⌃ Hide Chart"
                        : "⌄ Show Chart"}
                    </button>

                    {/* VIEW PRODUCT */}
                    <a
                      href={product.productUrl}
                      target="_blank"
                      rel="noreferrer"
                      className="view-product-button"
                    >
                      ↗ View Product
                    </a>

                    {/* REMOVE */}
                    <button
                      type="button"
                      className="remove-button"
                      onClick={() =>
                        setProductToRemove(product)
                      }
                      disabled={
                        removingProductId ===
                        product.id
                      }
                    >
                      {removingProductId ===
                      product.id
                        ? "Removing..."
                        : "🗑 Remove"}
                    </button>

                  </div>

                  {/* PRICE HISTORY CHART */}
                  {isExpanded && (
                    <div className="chart-container">

                      {/* CHART HEADER */}
                      <div className="chart-header">
                        <div>
                          <h4>
                            Price History
                          </h4>

                          <p>
                            Track how this product's
                            price changes over time.
                          </p>
                        </div>
                      </div>

                      {/* HISTORY LOADING */}
                      {historyLoading[
                        product.id
                      ] && (
                        <div className="chart-placeholder">
                          Loading price history...
                        </div>
                      )}

                      {/* HISTORY ERROR */}
                      {historyError[
                        product.id
                      ] && (
                        <div className="chart-error">
                          {
                            historyError[
                              product.id
                            ]
                          }
                        </div>
                      )}

                      {/* EMPTY HISTORY */}
                      {!historyLoading[
                        product.id
                      ] &&
                        !historyError[
                          product.id
                        ] &&
                        chartData.length === 0 && (
                          <div className="chart-placeholder">
                            No price history available
                            yet.
                          </div>
                        )}

                      {/* CHART */}
                      {!historyLoading[
                        product.id
                      ] &&
                        !historyError[
                          product.id
                        ] &&
                        chartData.length > 0 && (
                          <div className="price-chart-wrapper">

                            <ResponsiveContainer
                              width="100%"
                              height={220}
                            >
                              <LineChart
                                data={chartData}
                                margin={{
                                  top: 10,
                                  right: 12,
                                  left: -10,
                                  bottom: 0,
                                }}
                              >

                                <CartesianGrid
                                  strokeDasharray="3 3"
                                  stroke="#eadfda"
                                  vertical={false}
                                />

                                <XAxis
                                  dataKey="date"
                                  tick={{
                                    fill: "#64748b",
                                    fontSize: 11,
                                  }}
                                  tickLine={false}
                                  axisLine={{
                                    stroke:
                                      "#e2e8f0",
                                  }}
                                />

                                <YAxis
                                  dataKey="price"
                                  tick={{
                                    fill: "#64748b",
                                    fontSize: 11,
                                  }}
                                  tickLine={false}
                                  axisLine={false}
                                  width={60}
                                  tickFormatter={(value) =>
                                    Number(
                                      value
                                    ).toLocaleString(
                                      "en-IN"
                                    )
                                  }
                                />

                                <Tooltip
                                  formatter={(value) =>
                                    formatCurrency(
                                      value,
                                      product.currencyCode
                                    )
                                  }
                                  labelFormatter={(
                                    _,
                                    payload
                                  ) =>
                                    payload?.[0]
                                      ?.payload
                                      ?.fullDate || ""
                                  }
                                  contentStyle={{
                                    backgroundColor:
                                      "#ffffff",
                                    border:
                                      "1px solid #f0d8cf",
                                    borderRadius:
                                      "10px",
                                    boxShadow:
                                      "0 8px 20px rgba(0, 0, 0, 0.08)",
                                    fontSize:
                                      "13px",
                                  }}
                                  labelStyle={{
                                    color:
                                      "#334155",
                                    fontWeight: 600,
                                  }}
                                />

                                <Line
                                  type="monotone"
                                  dataKey="price"
                                  name="Price"
                                  stroke="#e85d3f"
                                  strokeWidth={3}
                                  dot={{
                                    r: 3,
                                    fill: "#e85d3f",
                                    stroke:
                                      "#ffffff",
                                    strokeWidth: 2,
                                  }}
                                  activeDot={{
                                    r: 6,
                                    fill: "#e85d3f",
                                    stroke:
                                      "#ffffff",
                                    strokeWidth: 3,
                                  }}
                                />

                              </LineChart>
                            </ResponsiveContainer>

                          </div>
                        )}

                    </div>
                  )}

                </article>
              );
            })}

          </div>
        )}

      </section>

      {/* REMOVE CONFIRMATION MODAL */}
      {productToRemove && (
        <div
          className="remove-modal-overlay"
          onClick={() => {
            if (!removingProductId) {
              setProductToRemove(null);
            }
          }}
        >
          <div
            className="remove-modal"
            onClick={(event) =>
              event.stopPropagation()
            }
          >

            <div className="remove-modal-icon">
              🗑
            </div>

            <h3>
              Stop tracking this product?
            </h3>

            <p>
              Are you sure you want to remove{" "}
              <strong>
                {
                  productToRemove.productName
                }
              </strong>{" "}
              from your tracked products?
            </p>

            <p className="remove-modal-warning">
              This will also remove its stored
              price history.
            </p>

            <div className="remove-modal-actions">

              <button
                type="button"
                className="remove-modal-cancel"
                onClick={() =>
                  setProductToRemove(null)
                }
                disabled={
                  removingProductId !== null
                }
              >
                Cancel
              </button>

              <button
                type="button"
                className="remove-modal-confirm"
                onClick={handleRemove}
                disabled={
                  removingProductId !== null
                }
              >
                {removingProductId !== null
                  ? "Removing..."
                  : "🗑 Remove Product"}
              </button>

            </div>

          </div>
        </div>
      )}
    </>
  );
}

export default TrackedProducts;