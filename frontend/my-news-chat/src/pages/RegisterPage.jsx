import { useEffect, useRef, useState } from "react";
import axios from "axios";
import { Link, useNavigate } from "react-router-dom";
import { API_CONFIG } from "../constants/config";

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
    <div className="app-shell flex min-h-screen items-center justify-center px-4 py-8">
      <div className="intel-card w-full max-w-xl p-6 sm:p-8">
        <p className="intel-kicker mb-3">Secure onboarding</p>
        <h1 className="text-[2.2rem] font-black tracking-[-0.08em] text-zinc-950">INTEL_CORE</h1>
        <p className="mt-2 text-sm font-medium text-zinc-600">
          {step === "details" ? "Create Account" : "Verify Signup"}
        </p>

        {error && (
          <div className="mt-5 rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-semibold text-red-700" role="alert">
            {error}
          </div>
        )}
        {success && (
          <div className="mt-5 rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm font-semibold text-emerald-700" aria-live="polite">
            {success}
          </div>
        )}

        {step === "otp" && (
          <div className="mt-5 rounded-2xl border border-black/10 bg-white/70 px-4 py-3 text-sm leading-6 text-zinc-700">
            Verifying <strong>{formData.email}</strong>. Enter the OTP to finish
            creating your account.
          </div>
        )}

        {debugOtp && step === "otp" && (
          <div className="mt-4 rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm font-semibold text-amber-700">
            Debug OTP: <strong>{debugOtp}</strong>
          </div>
        )}

        <form className="mt-6 space-y-4" onSubmit={handleSubmit}>
          {step === "details" ? (
            <>
              <input
                placeholder="USERNAME"
                value={formData.username}
                onChange={handleChange("username")}
                disabled={isLoading}
                className="intel-input"
                autoComplete="username"
                required
              />
              <input
                type="email"
                placeholder="EMAIL ADDRESS"
                value={formData.email}
                onChange={handleChange("email")}
                disabled={isLoading}
                className="intel-input"
                autoComplete="email"
                required
              />
              <input
                type="password"
                placeholder="PASSWORD"
                value={formData.password}
                onChange={handleChange("password")}
                disabled={isLoading}
                className="intel-input"
                autoComplete="new-password"
                required
              />
              <div className="rounded-[1.25rem] border border-black/10 bg-white/75 p-4">
                <div className="intel-kicker mb-3">Password requirements</div>
                <ul className="space-y-2 text-sm leading-6 text-zinc-600">
                  {PASSWORD_REQUIREMENTS.map((requirement) => (
                    <li key={requirement}>{requirement}</li>
                  ))}
                </ul>
                {formData.password && passwordError && (
                  <div className="mt-3 rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-semibold text-red-700">
                    {passwordError}
                  </div>
                )}
              </div>
            </>
          ) : (
            <input
              placeholder="ENTER OTP"
              value={otp}
              onChange={(event) => setOtp(event.target.value)}
              disabled={isLoading}
              className="intel-input"
              inputMode="numeric"
              autoComplete="one-time-code"
              required
            />
          )}

          <button
            type="submit"
            disabled={isLoading || (step === "details" && !!passwordError)}
            className="intel-button w-full"
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
          <div className="mt-4 flex flex-col gap-3 sm:flex-row">
            <button
              type="button"
              onClick={handleResendOtp}
              disabled={isLoading}
              className="intel-button-secondary flex-1"
            >
              RESEND OTP
            </button>
            <button
              type="button"
              onClick={handleEditDetails}
              disabled={isLoading}
              className="intel-button-secondary flex-1"
            >
              EDIT DETAILS
            </button>
          </div>
        )}

        <div className="mt-6 text-sm font-medium text-zinc-600">
          Already have an account?{" "}
          <Link
            to="/login"
            className="font-bold text-zinc-950 underline decoration-black/30 underline-offset-4 transition hover:decoration-black"
          >
            Sign In
          </Link>
        </div>
      </div>
    </div>
  );
}
