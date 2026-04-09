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

  const containerStyle = {
    display: 'flex',
    minHeight: '100vh',
    background: '#f8fafc',
    alignItems: 'center',
    justifyContent: 'center',
    fontFamily: '"Space Grotesk", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
    padding: '24px'
  };

  const cardStyle = {
    background: '#fff',
    padding: '48px',
    borderRadius: '0px',
    border: '4px solid #000',
    maxWidth: '400px',
    width: '100%',
    boxShadow: '0px 4px 12px rgba(0, 0, 0, 0.1)'
  };

  const headerStyle = {
    fontSize: '28px',
    fontWeight: '900',
    letterSpacing: '-1px',
    marginBottom: '8px',
    color: '#111827',
    textTransform: 'uppercase',
    margin: '0 0 24px 0'
  };

  const subtitleStyle = {
    fontSize: '12px',
    fontWeight: 'bold',
    opacity: 0.6,
    marginBottom: '32px',
    textTransform: 'uppercase',
    letterSpacing: '1px',
    color: '#666'
  };

  const inputStyle = {
    width: '100%',
    padding: '12px 16px',
    border: '2px solid #ddd',
    borderRadius: '6px',
    fontSize: '14px',
    fontFamily: 'inherit',
    marginBottom: '12px',
    boxSizing: 'border-box',
    transition: 'all 0.2s',
    backgroundColor: '#fff'
  };

  const inputFocusStyle = {
    ...inputStyle,
    borderColor: '#000',
    outline: 'none'
  };

  const buttonStyle = {
    width: '100%',
    padding: '12px 16px',
    border: '2px solid #000',
    borderRadius: '6px',
    background: '#000',
    color: '#fff',
    cursor: isLoading ? 'not-allowed' : 'pointer',
    fontWeight: '700',
    fontSize: '14px',
    transition: 'all 0.2s',
    textTransform: 'uppercase',
    fontFamily: 'inherit',
    letterSpacing: '0.5px',
    opacity: isLoading ? 0.7 : 1,
    marginTop: '8px'
  };

  const buttonHoverStyle = {
    ...buttonStyle,
    background: '#111827',
    transform: 'translateY(-2px)',
    boxShadow: '0px 4px 8px rgba(0, 0, 0, 0.2)'
  };

  const errorStyle = {
    color: '#dc2626',
    fontSize: '13px',
    padding: '10px 12px',
    background: '#fee2e2',
    border: '1px solid #fca5a5',
    borderRadius: '4px',
    marginBottom: '16px',
    fontWeight: '500'
  };

  const linkStyle = {
    color: '#000',
    textDecoration: 'none',
    fontWeight: '700',
    borderBottom: '2px solid #000',
    transition: 'all 0.2s'
  };

  const footerStyle = {
    marginTop: '24px',
    paddingTop: '24px',
    borderTop: '2px solid #e5e7eb',
    fontSize: '13px',
    color: '#666',
    textAlign: 'center'
  };

  return (
    <div style={containerStyle}>
      <div style={cardStyle}>
        <h1 style={headerStyle}>INTEL_CORE</h1>
        <p style={subtitleStyle}>Authentication</p>

        {error && <div style={errorStyle}>{error}</div>}

        <form onSubmit={handleSubmit}>
          <input
            placeholder="USERNAME"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            disabled={isLoading}
            style={inputStyle}
            onFocus={(e) => (e.target.style.borderColor = '#000')}
            onBlur={(e) => (e.target.style.borderColor = '#ddd')}
            required
          />
          <input
            type="password"
            placeholder="PASSWORD"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            disabled={isLoading}
            style={inputStyle}
            onFocus={(e) => (e.target.style.borderColor = '#000')}
            onBlur={(e) => (e.target.style.borderColor = '#ddd')}
            required
          />
          <button
            type="submit"
            disabled={isLoading}
            style={buttonStyle}
            onMouseEnter={(e) => {
              e.target.style.background = '#111827';
              e.target.style.transform = 'translateY(-2px)';
              e.target.style.boxShadow = '0px 4px 8px rgba(0, 0, 0, 0.2)';
            }}
            onMouseLeave={(e) => {
              e.target.style.background = '#000';
              e.target.style.transform = 'translateY(0)';
              e.target.style.boxShadow = 'none';
            }}
          >
            {isLoading ? "AUTHENTICATING..." : "SIGN IN"}
          </button>
        </form>

        <div style={footerStyle}>
          Don't have an account?{" "}
          <Link
            to="/register"
            style={linkStyle}
            onMouseEnter={(e) => (e.target.style.opacity = '0.7')}
            onMouseLeave={(e) => (e.target.style.opacity = '1')}
          >
            Register
          </Link>
        </div>
      </div>
    </div>
  );
}
