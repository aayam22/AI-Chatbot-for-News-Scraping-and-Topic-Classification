import { useState } from "react";
import axios from "axios";
import { useNavigate, Link } from "react-router-dom";
import { API_CONFIG } from '../constants/config';

/**
 * RegisterPage Component - User registration page
 * Handles registration form submission and redirects to login
 * Styled to match news chat theme
 */
export default function RegisterPage() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    setIsLoading(true);

    try {
      await axios.post(
        `${API_CONFIG.BACKEND_URL}/register`,
        { username, email, password },
        { headers: { "Content-Type": "application/json" } }
      );
      setSuccess("Registered successfully! Redirecting to login...");
      setTimeout(() => navigate("/login"), 1500);
    } catch (err) {
      setError(err.response?.data?.detail || "Registration failed");
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

  const successStyle = {
    color: '#059669',
    fontSize: '13px',
    padding: '10px 12px',
    background: '#d1fae5',
    border: '1px solid #6ee7b7',
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
        <p style={subtitleStyle}>Create Account</p>

        {error && <div style={errorStyle}>{error}</div>}
        {success && <div style={successStyle}>{success}</div>}

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
            type="email"
            placeholder="EMAIL ADDRESS"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
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
            {isLoading ? "CREATING ACCOUNT..." : "REGISTER"}
          </button>
        </form>

        <div style={footerStyle}>
          Already have an account?{" "}
          <Link
            to="/login"
            style={linkStyle}
            onMouseEnter={(e) => (e.target.style.opacity = '0.7')}
            onMouseLeave={(e) => (e.target.style.opacity = '1')}
          >
            Sign In
          </Link>
        </div>
      </div>
    </div>
  );
}
