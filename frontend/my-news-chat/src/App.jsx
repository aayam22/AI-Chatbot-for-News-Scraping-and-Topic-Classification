import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import ChatPage from "./pages/ChatPage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import AnalysisPage from "./pages/AnalysisPage";
import ArchivePage from "./pages/ArchivePage";
import { useCallback, useState } from "react";
import useAuth from "./hooks/useAuth";
import useChatMessages from "./hooks/useChatMessages";

function ProtectedRoute({ isAuthenticated, children }) {
  return isAuthenticated ? children : <Navigate to="/login" replace />;
}

function App() {
  const { token, setToken, logout } = useAuth();
  const {
    messages,
    setMessages,
    clearAllMessages,
    refreshMessages,
    removeMessage,
  } = useChatMessages(token);
  const [isCollapsed, setIsCollapsed] = useState(false);
  const isAuthenticated = Boolean(token);

  const handleLogout = useCallback(() => {
    clearAllMessages();
    logout();
  }, [clearAllMessages, logout]);

  return (
    <BrowserRouter>
      <div style={{ display: "flex", minHeight: "100vh" }}>
        {isAuthenticated && (
          <Sidebar
            onLogout={handleLogout}
            isCollapsed={isCollapsed}
            setIsCollapsed={setIsCollapsed}
          />
        )}
        <div
          style={{
            flex: 1,
            display: "flex",
            flexDirection: "column",
            overflow: "auto",
            marginLeft: isAuthenticated ? (isCollapsed ? "80px" : "260px") : "0px",
            transition: "margin-left 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
          }}
        >
          <Routes>
            {/* Public Routes */}
            <Route path="/login" element={<LoginPage setToken={setToken} />} />
            <Route path="/register" element={<RegisterPage />} />

            {/* Private Routes */}
            <Route
              path="/"
              element={
                <ProtectedRoute isAuthenticated={isAuthenticated}>
                  <ChatPage
                    messages={messages}
                    setMessages={setMessages}
                    token={token}
                    refreshMessages={refreshMessages}
                  />
                </ProtectedRoute>
              }
            />
            <Route
              path="/analysis"
              element={
                <ProtectedRoute isAuthenticated={isAuthenticated}>
                  <AnalysisPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/archive"
              element={
                <ProtectedRoute isAuthenticated={isAuthenticated}>
                  <ArchivePage
                    token={token}
                    refreshMessages={refreshMessages}
                    removeMessage={removeMessage}
                  />
                </ProtectedRoute>
              }
            />
            <Route
              path="/system"
              element={
                <ProtectedRoute isAuthenticated={isAuthenticated}>
                  <h1>System Page</h1>
                </ProtectedRoute>
              }
            />

            {/* Catch-all redirect */}
            <Route
              path="*"
              element={
                isAuthenticated ? <Navigate to="/" replace /> : <Navigate to="/login" replace />
              }
            />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
}

export default App;
