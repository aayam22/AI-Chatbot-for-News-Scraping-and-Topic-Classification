import { useState } from "react";
import axios from "axios";
import { useNavigate, Link } from "react-router-dom";
import { API_CONFIG } from '../constants/config';

/**
 * LoginPage Component - User authentication page
 * Handles login form submission and token storage
 * Styled to match news chat theme
 */
export default function LoginPage({ setToken }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      const res = await axios.post(
        `${API_CONFIG.BACKEND_URL}/login`,
        { username, password },
        { headers: { "Content-Type": "application/json" } }
      );

      const token = res.data.access_token;
      if (!token) throw new Error("No token returned");

      setToken(token);
      navigate("/");
    } catch (err) {
      console.error(err);
      setError(
        err.response?.data?.detail || "Invalid credentials or server error"
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-shell flex min-h-screen items-center justify-center px-4 py-8">
      <div className="intel-card w-full max-w-md p-6 sm:p-8">
        <p className="intel-kicker mb-3">Access terminal</p>
        <h1 className="text-[2.2rem] font-black tracking-[-0.08em] text-zinc-950">INTEL_CORE</h1>
        <p className="mt-2 text-sm font-medium text-zinc-600">Authentication</p>

        {error && (
          <div className="mt-5 rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-semibold text-red-700">
            {error}
          </div>
        )}

        <form className="mt-6 space-y-4" onSubmit={handleSubmit}>
          <input
            placeholder="USERNAME"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            disabled={isLoading}
            className="intel-input"
            required
          />
          <input
            type="password"
            placeholder="PASSWORD"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            disabled={isLoading}
            className="intel-input"
            required
          />
          <button
            type="submit"
            disabled={isLoading}
            className="intel-button w-full"
          >
            {isLoading ? "AUTHENTICATING..." : "SIGN IN"}
          </button>
        </form>

        <div className="mt-6 text-sm font-medium text-zinc-600">
          Don't have an account?{" "}
          <Link
            to="/register"
            className="font-bold text-zinc-950 underline decoration-black/30 underline-offset-4 transition hover:decoration-black"
          >
            Register
          </Link>
        </div>
      </div>
    </div>
  );
}
