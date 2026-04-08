import { useState } from "react";
import axios from "axios";
import { useNavigate, Link } from "react-router-dom";

const BACKEND_URL = "http://127.0.0.1:8000";

export default function Login({ setToken }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(""); // Clear previous error
    try {
      const res = await axios.post(
        `${BACKEND_URL}/login`,
        { username, password },
        { headers: { "Content-Type": "application/json" } } // ensure JSON
      );

      const token = res.data.access_token;
      if (!token) throw new Error("No token returned");

      localStorage.setItem("token", token);
      setToken(token); // update App state
      navigate("/"); // redirect to chat page
    } catch (err) {
      console.error(err);
      setError(
        err.response?.data?.detail || "Invalid credentials or server error"
      );
    }
  };

  return (
    <div style={{ padding: "48px" }}>
      <h1>Login</h1>
      {error && <p style={{ color: "red" }}>{error}</p>}
      <form
        onSubmit={handleSubmit}
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "12px",
          maxWidth: "300px",
        }}
      >
        <input
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <button type="submit">Login</button>
      </form>
      <p>
        Don't have an account? <Link to="/register">Register</Link>
      </p>
    </div>
  );
}