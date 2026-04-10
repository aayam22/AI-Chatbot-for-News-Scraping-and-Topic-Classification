import { useState } from "react";
import axios from "axios";
import { useNavigate, Link } from "react-router-dom";
import { API_CONFIG } from '../constants/config';
import styles from './LoginPage.module.css';

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

      localStorage.setItem("token", token);
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
    <div className={styles.container}>
      <div className={styles.card}>
        <h1 className={styles.header}>INTEL_CORE</h1>
        <p className={styles.subtitle}>Authentication</p>

        {error && <div className={styles.error}>{error}</div>}

        <form className={styles.form} onSubmit={handleSubmit}>
          <input
            placeholder="USERNAME"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            disabled={isLoading}
            className={styles.input}
            required
          />
          <input
            type="password"
            placeholder="PASSWORD"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            disabled={isLoading}
            className={styles.input}
            required
          />
          <button
            type="submit"
            disabled={isLoading}
            className={styles.button}
          >
            {isLoading ? "AUTHENTICATING..." : "SIGN IN"}
          </button>
        </form>

        <div className={styles.footer}>
          Don't have an account?{" "}
          <Link
            to="/register"
            className={styles.link}
          >
            Register
          </Link>
        </div>
      </div>
    </div>
  );
}
