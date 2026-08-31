import { useEffect, useState } from "react";

import Header from "./components/Header.jsx";
import Hero from "./components/Hero.jsx";
import AuthModal from "./components/AuthModal.jsx";
import FeatureSection from "./components/FeatureSection.jsx";
import Footer from "./components/Footer.jsx";
import TrackedProducts from "./components/TrackedProducts.jsx";

import { apiRequest } from "./api/client";

// =========================================================
// INITIAL THEME
// =========================================================

function getInitialTheme() {
  if (typeof window === "undefined") {
    return "light";
  }

  const stored = window.localStorage.getItem(
    "dealdrop-theme"
  );

  if (stored === "light" || stored === "dark") {
    return stored;
  }

  return window.matchMedia?.(
    "(prefers-color-scheme: dark)"
  ).matches
    ? "dark"
    : "light";
}

// =========================================================
// APP
// =========================================================

export default function App() {
  const [theme, setTheme] = useState(getInitialTheme);

  const [user, setUser] = useState(null);

  // Supported modes:
  // "signin"
  // "signup"
  // "forgot-password"
  const [authModal, setAuthModal] = useState(null);

  // Used to refresh tracked products after
  // successfully tracking a new product
  const [refreshProducts, setRefreshProducts] =
    useState(0);

  // =========================================================
  // THEME
  // =========================================================

  useEffect(() => {
    document.documentElement.setAttribute(
      "data-theme",
      theme
    );

    window.localStorage.setItem(
      "dealdrop-theme",
      theme
    );
  }, [theme]);

  // =========================================================
  // RESTORE USER AFTER PAGE REFRESH
  // =========================================================

  useEffect(() => {
    async function restoreUser() {
      const token = localStorage.getItem(
        "access_token"
      );

      // No token means user is not logged in
      if (!token) {
        return;
      }

      try {
        const userData = await apiRequest(
          "/auth/me"
        );

        setUser(userData);
      } catch (error) {
        console.error(
          "Failed to restore user:",
          error
        );

        // Invalid/expired token
        localStorage.removeItem("access_token");

        setUser(null);
      }
    }

    restoreUser();
  }, []);

  // =========================================================
  // TOGGLE THEME
  // =========================================================

  function toggleTheme() {
    setTheme((previousTheme) =>
      previousTheme === "light"
        ? "dark"
        : "light"
    );
  }

  // =========================================================
  // AUTH SUCCESS
  // =========================================================

  function handleAuthSuccess(userData) {
    setUser(userData);

    setAuthModal(null);
  }

  // =========================================================
  // SIGN OUT
  // =========================================================

  function handleSignOut() {
    localStorage.removeItem("access_token");

    setUser(null);

    setRefreshProducts(0);
  }

  // =========================================================
  // PRODUCT TRACKED SUCCESSFULLY
  // =========================================================

  function handleProductTracked() {
    // Change value to trigger TrackedProducts useEffect
    setRefreshProducts(
      (previousValue) => previousValue + 1
    );
  }

  // =========================================================
  // AUTH MODAL MODE SWITCH
  // =========================================================

  function handleAuthModeSwitch(newMode) {
    // If AuthModal explicitly provides a mode,
    // use that mode.
    //
    // This is needed for:
    // signin -> forgot-password
    // forgot-password -> signin
    // signup -> signin

    if (newMode) {
      setAuthModal(newMode);
      return;
    }

    // Normal Sign In <-> Sign Up switching
    setAuthModal(
      authModal === "signin"
        ? "signup"
        : "signin"
    );
  }

  // =========================================================
  // UI
  // =========================================================

  return (
    <div className="app">
      {/* =====================================================
          HEADER
          ===================================================== */}

      <Header
        theme={theme}
        onToggleTheme={toggleTheme}
        user={user}
        onOpenSignIn={() =>
          setAuthModal("signin")
        }
        onOpenSignUp={() =>
          setAuthModal("signup")
        }
        onSignOut={handleSignOut}
      />

      <main>
        {/* ===================================================
            HERO
            =================================================== */}

        <Hero
          user={user}

          // If unauthenticated user tries to track,
          // open the signup modal
          onRequireAuth={() =>
            setAuthModal("signup")
          }

          // Refresh tracked products after success
          onProductTracked={handleProductTracked}
        />

        {/* ===================================================
            AUTHENTICATED / UNAUTHENTICATED CONTENT
            =================================================== */}

        {user ? (
          <TrackedProducts
            refreshTrigger={refreshProducts}
          />
        ) : (
          <FeatureSection
            onOpenSignUp={() =>
              setAuthModal("signup")
            }
          />
        )}
      </main>

      {/* =====================================================
          FOOTER
          ===================================================== */}

      <Footer />

      {/* =====================================================
          AUTH MODAL
          ===================================================== */}

      {authModal && (
        <AuthModal
          mode={authModal}

          onClose={() =>
            setAuthModal(null)
          }

          // Supports:
          // - Sign In -> Sign Up
          // - Sign Up -> Sign In
          // - Sign In -> Forgot Password
          // - Forgot Password -> Sign In
          onSwitchMode={handleAuthModeSwitch}

          onAuthSuccess={handleAuthSuccess}
        />
      )}
    </div>
  );
}