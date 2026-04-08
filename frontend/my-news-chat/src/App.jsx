import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import NewsChat from "./components/NewsChat";
import Login from "./components/Login";
import Register from "./components/Register";
import { useState, useEffect } from "react";

function App() {
  const [messages, setMessages] = useState([]);
  const [token, setToken] = useState(localStorage.getItem("token") || null);

  // Load messages from localStorage on mount
  useEffect(() => {
    const savedMessages = localStorage.getItem("chat_messages");
    if (savedMessages) setMessages(JSON.parse(savedMessages));
  }, []);

  // Save messages to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem("chat_messages", JSON.stringify(messages));
  }, [messages]);

  // Private Route wrapper
  const PrivateRoute = ({ children }) => {
    return token ? children : <Navigate to="/login" replace />;
  };

  return (
    <BrowserRouter>
      <div style={{ display: "flex", minHeight: "100vh" }}>
        {token && <Sidebar setToken={setToken} />} {/* Show sidebar only if logged in */}
        <div style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "auto" }}>
          <Routes>
            {/* Public Routes */}
            <Route path="/login" element={<Login setToken={setToken} />} />
            <Route path="/register" element={<Register />} />

            {/* Private Routes */}
            <Route 
              path="/" 
              element={
                <PrivateRoute>
                  <NewsChat messages={messages} setMessages={setMessages} />
                </PrivateRoute>
              } 
            />
            <Route 
              path="/analysis" 
              element={
                <PrivateRoute>
                  <h1>Analysis Page</h1>
                </PrivateRoute>
              } 
            />
            <Route 
              path="/archive" 
              element={
                <PrivateRoute>
                  <h1>Archive Page</h1>
                </PrivateRoute>
              } 
            />
            <Route 
              path="/system" 
              element={
                <PrivateRoute>
                  <h1>System Page</h1>
                </PrivateRoute>
              } 
            />

            {/* Catch-all redirect */}
            <Route path="*" element={token ? <Navigate to="/" /> : <Navigate to="/login" />} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
}

export default App;