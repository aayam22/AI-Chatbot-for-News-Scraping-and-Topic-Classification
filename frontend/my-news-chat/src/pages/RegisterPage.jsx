import { useEffect, useRef, useState } from "react";
import axios from "axios";
import { Link, useNavigate } from "react-router-dom";
import { API_CONFIG } from "../constants/config";
import styles from "./RegisterPage.module.css";

const initialFormState = {
  username: "",
  email: "",
  password: "",
};

const PASSWORD_REQUIREMENTS = [
  "Use at least 12 characters.",
  "Avoid common passwords such as password123 or 123456789.",
  "Do not include your username or email.",
  "Use a mix of uppercase, lowercase, numbers, and symbols.",
];

function getErrorMessage(error, fallbackMessage) {
  return error.response?.data?.detail || fallbackMessage;
}

function getPasswordValidation(password, username, email) {
  const normalizedPassword = password.toLowerCase();
  const compactPassword = normalizedPassword.replace(/[^a-z0-9]/g, "");
  const personalTokens = `${username} ${email}`
    .toLowerCase()
    .split(/[^a-z0-9]+/)
    .filter((token) => token.length >= 3);

  const commonPasswords = new Set([
    "123456",
    "12345678",
    "123456789",
    "1234567890",
    "abc123",
    "admin123",
    "letmein",
    "passw0rd",
    "password",
    "password1",
    "password123",
    "qwerty",
    "qwerty123",
    "welcome",
  ]);

  if (password.length < 12) {
    return "Password must be at least 12 characters long.";
  }

  if (!password.trim()) {
    return "Password cannot be empty or only spaces.";
  }

  if (commonPasswords.has(normalizedPassword) || commonPasswords.has(compactPassword)) {
    return "Password is too common. Choose a more unique password.";
  }

  if (personalTokens.some((token) => compactPassword.includes(token))) {
    return "Password must not contain your username or email.";
  }

  if (/^(.)\1{7,}$/.test(password)) {
    return "Password cannot repeat the same character many times.";
  }

  const hasLower = /[a-z]/.test(password);
  const hasUpper = /[A-Z]/.test(password);
  const hasDigit = /\d/.test(password);
  const hasSymbol = /[^A-Za-z0-9]/.test(password);

  if ([hasLower, hasUpper, hasDigit, hasSymbol].filter(Boolean).length < 3) {
    return "Password should use at least three of these: lowercase, uppercase, numbers, symbols.";
  }

  return "";
}

/**
 * RegisterPage Component - Two-step signup with OTP verification
 */
export default function RegisterPage() {
  const [formData, setFormData] = useState(initialFormState);
  const [otp, setOtp] = useState("");
  const [step, setStep] = useState("details");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [debugOtp, setDebugOtp] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const redirectTimeoutRef = useRef(null);
  const navigate = useNavigate();
  const passwordError = getPasswordValidation(
    formData.password,
    formData.username,
    formData.email
  );

  useEffect(() => {
    return () => {
      if (redirectTimeoutRef.current) {
        clearTimeout(redirectTimeoutRef.current);
      }
    };
  }, []);

  const handleChange = (field) => (event) => {
    setFormData((current) => ({
      ...current,
      [field]: event.target.value,
    }));
  };

  const requestOtp = async (endpoint = "/register/request-otp") => {
    const response = await axios.post(
      `${API_CONFIG.BACKEND_URL}${endpoint}`,
      formData,
      { headers: { "Content-Type": "application/json" } }
    );

    const detailMessage =
      response.data.delivery === "debug"
        ? "OTP generated in debug mode. Use the code below or check the API logs."
        : `We sent a verification code to ${response.data.email}.`;

    setStep("otp");
    setOtp("");
    setDebugOtp(response.data.debug_otp || "");
    setSuccess(`${response.data.message} ${detailMessage}`);
  };

  const verifyOtp = async () => {
    await axios.post(
      `${API_CONFIG.BACKEND_URL}/register`,
      {
        username: formData.username,
        email: formData.email,
        otp,
      },
      { headers: { "Content-Type": "application/json" } }
    );

    setSuccess("Account verified and created successfully! Redirecting to login...");

    redirectTimeoutRef.current = setTimeout(() => {
      navigate("/login");
    }, 1500);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setSuccess("");

    if (step === "details" && passwordError) {
      setError(passwordError);
      return;
    }

    setIsLoading(true);

    try {
      if (step === "details") {
        await requestOtp();
        return;
      }

      await verifyOtp();
    } catch (err) {
      setError(getErrorMessage(err, "Registration failed"));
    } finally {
      setIsLoading(false);
    }
  };

  const handleResendOtp = async () => {
    setError("");
    setSuccess("");
    setIsLoading(true);

    try {
      await requestOtp("/register/resend-otp");
    } catch (err) {
      setError(getErrorMessage(err, "Unable to resend verification code"));
    } finally {
      setIsLoading(false);
    }
  };

  const handleEditDetails = () => {
    setStep("details");
    setOtp("");
    setDebugOtp("");
    setError("");
    setSuccess("");
  };

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <h1 className={styles.header}>INTEL_CORE</h1>
        <p className={styles.subtitle}>
          {step === "details" ? "Create Account" : "Verify Signup"}
        </p>

        {error && (
          <div className={styles.error} role="alert">
            {error}
          </div>
        )}
        {success && (
          <div className={styles.success} aria-live="polite">
            {success}
          </div>
        )}

        {step === "otp" && (
          <div className={styles.infoBox}>
            Verifying <strong>{formData.email}</strong>. Enter the OTP to finish
            creating your account.
          </div>
        )}

        {debugOtp && step === "otp" && (
          <div className={styles.debugBox}>
            Debug OTP: <strong>{debugOtp}</strong>
          </div>
        )}

        <form className={styles.form} onSubmit={handleSubmit}>
          {step === "details" ? (
            <>
              <input
                placeholder="USERNAME"
                value={formData.username}
                onChange={handleChange("username")}
                disabled={isLoading}
                className={styles.input}
                autoComplete="username"
                required
              />
              <input
                type="email"
                placeholder="EMAIL ADDRESS"
                value={formData.email}
                onChange={handleChange("email")}
                disabled={isLoading}
                className={styles.input}
                autoComplete="email"
                required
              />
              <input
                type="password"
                placeholder="PASSWORD"
                value={formData.password}
                onChange={handleChange("password")}
                disabled={isLoading}
                className={styles.input}
                autoComplete="new-password"
                required
              />
              <div className={styles.passwordPanel}>
                <div className={styles.passwordHeading}>Password requirements</div>
                <ul className={styles.passwordList}>
                  {PASSWORD_REQUIREMENTS.map((requirement) => (
                    <li key={requirement}>{requirement}</li>
                  ))}
                </ul>
                {formData.password && passwordError && (
                  <div className={styles.passwordError}>{passwordError}</div>
                )}
              </div>
            </>
          ) : (
            <input
              placeholder="ENTER OTP"
              value={otp}
              onChange={(event) => setOtp(event.target.value)}
              disabled={isLoading}
              className={styles.input}
              inputMode="numeric"
              autoComplete="one-time-code"
              required
            />
          )}

          <button
            type="submit"
            disabled={isLoading || (step === "details" && !!passwordError)}
            className={styles.button}
          >
            {isLoading
              ? step === "details"
                ? "SENDING OTP..."
                : "VERIFYING OTP..."
              : step === "details"
                ? "SEND OTP"
                : "VERIFY & CREATE ACCOUNT"}
          </button>
        </form>

        {step === "otp" && (
          <div className={styles.actionRow}>
            <button
              type="button"
              onClick={handleResendOtp}
              disabled={isLoading}
              className={`${styles.button} ${styles.secondaryButton}`}
            >
              RESEND OTP
            </button>
            <button
              type="button"
              onClick={handleEditDetails}
              disabled={isLoading}
              className={`${styles.button} ${styles.secondaryButton}`}
            >
              EDIT DETAILS
            </button>
          </div>
        )}

        <div className={styles.footer}>
          Already have an account?{" "}
          <Link to="/login" className={styles.link}>
            Sign In
          </Link>
        </div>
      </div>
    </div>
  );
}
