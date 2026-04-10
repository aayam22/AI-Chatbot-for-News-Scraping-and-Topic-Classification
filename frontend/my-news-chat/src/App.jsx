import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import ChatPage from "./pages/ChatPage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import AnalysisPage from "./pages/AnalysisPage";
import { useState, useEffect } from "react";
import { STORAGE_KEYS } from "./constants/config";

function App() {
  const [messages, setMessages] = useState([]);
  const [token, setToken] = useState(localStorage.getItem(STORAGE_KEYS.TOKEN) || null);
  const [isCollapsed, setIsCollapsed] = useState(false);

  // Load messages from localStorage on mount
  useEffect(() => {
    const savedMessages = localStorage.getItem(STORAGE_KEYS.CHAT_MESSAGES);
    if (savedMessages) setMessages(JSON.parse(savedMessages));
  }, []);

  // Save messages to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem(STORAGE_KEYS.CHAT_MESSAGES, JSON.stringify(messages));
  }, [messages]);

  // Private Route wrapper
  const PrivateRoute = ({ children }) => {
    return token ? children : <Navigate to="/login" replace />;
  };

  return (
    <BrowserRouter>
      <div style={{ display: "flex", minHeight: "100vh" }}>
        {token && <Sidebar setToken={setToken} isCollapsed={isCollapsed} setIsCollapsed={setIsCollapsed} />}
        <div style={{ 
          flex: 1, 
          display: "flex", 
          flexDirection: "column", 
          overflow: "auto",
          marginLeft: token ? (isCollapsed ? '80px' : '260px') : '0px',
          transition: 'margin-left 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
        }}>
          <Routes>
            {/* Public Routes */}
            <Route path="/login" element={<LoginPage setToken={setToken} />} />
            <Route path="/register" element={<RegisterPage />} />

            {/* Private Routes */}
            <Route 
              path="/" 
              element={
                <PrivateRoute>
                  <ChatPage messages={messages} setMessages={setMessages} />
                </PrivateRoute>
              } 
            />
            <Route 
              path="/analysis" 
              element={
                <PrivateRoute>
                  <AnalysisPage />
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