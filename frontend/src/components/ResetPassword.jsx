import { useState } from "react";
import {
  useNavigate,
  useSearchParams,
} from "react-router-dom";

import { apiRequest } from "../api/client";

export default function ResetPassword() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const token = searchParams.get("token");

  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] =
    useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  function getErrorMessage(error) {
    if (!error) {
      return "Unable to reset your password.";
    }

    if (typeof error === "string") {
      return error;
    }

    if (typeof error.message === "string") {
      return error.message;
    }

    if (Array.isArray(error)) {
      return error
        .map((item) => {
          if (typeof item === "string") {
            return item;
          }

          if (item?.msg) {
            return item.msg;
          }

          return JSON.stringify(item);
        })
        .join(", ");
    }

    if (typeof error === "object") {
      if (error.detail) {
        if (typeof error.detail === "string") {
          return error.detail;
        }

        if (Array.isArray(error.detail)) {
          return error.detail
            .map((item) => {
              if (typeof item === "string") {
                return item;
              }

              return (
                item?.msg ||
                JSON.stringify(item)
              );
            })
            .join(", ");
        }

        return JSON.stringify(error.detail);
      }

      return JSON.stringify(error);
    }

    return String(error);
  }

  async function handleSubmit(event) {
    event.preventDefault();

    setError("");
    setSuccess("");

    if (!token) {
      setError(
        "This password reset link is invalid or missing a token."
      );
      return;
    }

    if (password.length < 8) {
      setError(
        "Password must be at least 8 characters long."
      );
      return;
    }

    if (password.length > 100) {
      setError(
        "Password must not exceed 100 characters."
      );
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    try {
      setLoading(true);

      const response = await apiRequest(
        "/auth/reset-password",
        {
          method: "POST",
          body: JSON.stringify({
            token,
            new_password: password,
          }),
        }
      );

      console.log(
        "Password reset response:",
        response
      );

      setSuccess(
        response?.message ||
          "Your password has been reset successfully."
      );

      setPassword("");
      setConfirmPassword("");

      setTimeout(() => {
        navigate("/");
      }, 2000);
    } catch (error) {
      console.error(
        "Password reset failed:",
        error
      );

      setError(
        getErrorMessage(error)
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "40px 20px",
        boxSizing: "border-box",
        backgroundColor:
          "var(--page-bg, #faf9f7)",
      }}
    >
      <div
        style={{
          width: "100%",
          maxWidth: "460px",
          backgroundColor:
            "var(--card-bg, #ffffff)",
          borderRadius: "16px",
          padding: "40px",
          boxSizing: "border-box",
          border:
            "1px solid var(--border-color, #e5e7eb)",
          boxShadow:
            "0 10px 30px rgba(0, 0, 0, 0.08)",
        }}
      >
        {/* LOGO */}
        <div
          style={{
            textAlign: "center",
            marginBottom: "30px",
          }}
        >
          <h1
            style={{
              margin: "0 0 10px",
              fontSize: "30px",
              fontWeight: "700",
              color: "#ff5a1f",
            }}
          >
            DealDrop
          </h1>

          <h2
            style={{
              margin: "0 0 10px",
              fontSize: "24px",
              color:
                "var(--text-color, #111827)",
            }}
          >
            Reset your password
          </h2>

          <p
            style={{
              margin: 0,
              color:
                "var(--muted-text, #6b7280)",
              fontSize: "14px",
              lineHeight: "1.5",
            }}
          >
            Enter a new password for your
            DealDrop account.
          </p>
        </div>

        {/* ERROR */}
        {error && (
          <div
            style={{
              backgroundColor: "#fee2e2",
              color: "#b91c1c",
              border:
                "1px solid #fecaca",
              borderRadius: "8px",
              padding: "12px 14px",
              marginBottom: "20px",
              fontSize: "14px",
              lineHeight: "1.5",
              wordBreak: "break-word",
            }}
          >
            {error}
          </div>
        )}

        {/* SUCCESS */}
        {success && (
          <div
            style={{
              backgroundColor: "#dcfce7",
              color: "#166534",
              border:
                "1px solid #bbf7d0",
              borderRadius: "8px",
              padding: "12px 14px",
              marginBottom: "20px",
              fontSize: "14px",
              lineHeight: "1.5",
            }}
          >
            {success}
          </div>
        )}

        {!success && (
          <form onSubmit={handleSubmit}>
            {/* NEW PASSWORD */}
            <div
              style={{
                marginBottom: "20px",
              }}
            >
              <label
                htmlFor="password"
                style={{
                  display: "block",
                  marginBottom: "8px",
                  fontSize: "14px",
                  fontWeight: "600",
                  color:
                    "var(--text-color, #111827)",
                }}
              >
                New Password
              </label>

              <input
                id="password"
                type="password"
                value={password}
                onChange={(event) => {
                  setPassword(
                    event.target.value
                  );
                  setError("");
                }}
                placeholder="Enter your new password"
                minLength={8}
                maxLength={100}
                autoComplete="new-password"
                disabled={loading}
                required
                style={{
                  width: "100%",
                  boxSizing: "border-box",
                  padding: "13px 14px",
                  borderRadius: "8px",
                  border:
                    "1px solid #d1d5db",
                  fontSize: "15px",
                  outline: "none",
                  backgroundColor:
                    "#ffffff",
                  color: "#111827",
                }}
              />

              <p
                style={{
                  margin: "7px 0 0",
                  fontSize: "12px",
                  color:
                    "var(--muted-text, #6b7280)",
                }}
              >
                Must be between 8 and 100
                characters.
              </p>
            </div>

            {/* CONFIRM PASSWORD */}
            <div
              style={{
                marginBottom: "25px",
              }}
            >
              <label
                htmlFor="confirm-password"
                style={{
                  display: "block",
                  marginBottom: "8px",
                  fontSize: "14px",
                  fontWeight: "600",
                  color:
                    "var(--text-color, #111827)",
                }}
              >
                Confirm New Password
              </label>

              <input
                id="confirm-password"
                type="password"
                value={confirmPassword}
                onChange={(event) => {
                  setConfirmPassword(
                    event.target.value
                  );
                  setError("");
                }}
                placeholder="Confirm your new password"
                minLength={8}
                maxLength={100}
                autoComplete="new-password"
                disabled={loading}
                required
                style={{
                  width: "100%",
                  boxSizing: "border-box",
                  padding: "13px 14px",
                  borderRadius: "8px",
                  border:
                    "1px solid #d1d5db",
                  fontSize: "15px",
                  outline: "none",
                  backgroundColor:
                    "#ffffff",
                  color: "#111827",
                }}
              />
            </div>

            {/* RESET BUTTON */}
            <button
              type="submit"
              disabled={loading || !token}
              style={{
                width: "100%",
                border: "none",
                borderRadius: "8px",
                padding: "14px",
                backgroundColor:
                  loading || !token
                    ? "#fca98a"
                    : "#ff5a1f",
                color: "#ffffff",
                fontSize: "16px",
                fontWeight: "700",
                cursor:
                  loading || !token
                    ? "not-allowed"
                    : "pointer",
              }}
            >
              {loading
                ? "Resetting Password..."
                : "Reset Password"}
            </button>
          </form>
        )}

        {/* BACK */}
        <div
          style={{
            textAlign: "center",
            marginTop: "25px",
          }}
        >
          <button
            type="button"
            onClick={() => navigate("/")}
            style={{
              border: "none",
              background: "transparent",
              color: "#ff5a1f",
              fontSize: "14px",
              fontWeight: "600",
              cursor: "pointer",
            }}
          >
            ← Back to DealDrop
          </button>
        </div>
      </div>
    </div>
  );
}