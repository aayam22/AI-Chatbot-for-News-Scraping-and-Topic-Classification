import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import ChatPage from "./pages/ChatPage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import AnalysisPage from "./pages/AnalysisPage";
import ArchivePage from "./pages/ArchivePage";
import SettingsPage from "./pages/SettingsPage";
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
    clearVisibleMessages,
    clearAllMessages,
    refreshMessages,
    removeMessage,
  } = useChatMessages(token);
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false);
  const isAuthenticated = Boolean(token);

  const handleLogout = useCallback(() => {
    clearAllMessages();
    setIsMobileSidebarOpen(false);
    logout();
  }, [clearAllMessages, logout]);

  return (
    <BrowserRouter>
      <div className="app-shell flex min-h-screen">
        {isAuthenticated && (
          <div
            className={`fixed inset-0 z-30 bg-black/35 transition-opacity duration-300 lg:hidden ${
              isMobileSidebarOpen ? "pointer-events-auto opacity-100" : "pointer-events-none opacity-0"
            }`}
            onClick={() => setIsMobileSidebarOpen(false)}
          />
        )}

        {isAuthenticated && (
          <Sidebar
            onLogout={handleLogout}
            isCollapsed={isCollapsed}
            setIsCollapsed={setIsCollapsed}
            isMobileOpen={isMobileSidebarOpen}
            onMobileClose={() => setIsMobileSidebarOpen(false)}
            onNavigate={() => setIsMobileSidebarOpen(false)}
          />
        )}

        {isAuthenticated && (
          <button
            type="button"
            onClick={() => setIsMobileSidebarOpen((current) => !current)}
            className="fixed bottom-5 left-5 z-50 rounded-full border-2 border-black bg-white px-4 py-3 text-[11px] font-extrabold uppercase tracking-[0.16em] text-zinc-950 shadow-[8px_8px_0_rgba(0,0,0,0.08)] transition hover:-translate-y-0.5 lg:hidden"
          >
            {isMobileSidebarOpen ? "Close" : "Menu"}
          </button>
        )}

        <div
          className={`flex min-h-screen flex-1 flex-col overflow-x-hidden transition-[padding] duration-300 ${
            isAuthenticated ? (isCollapsed ? "lg:pl-20" : "lg:pl-[16.25rem]") : ""
          }`}
        >
          <Routes>
            <Route path="/login" element={<LoginPage setToken={setToken} />} />
            <Route path="/register" element={<RegisterPage />} />

            <Route
              path="/"
              element={
                <ProtectedRoute isAuthenticated={isAuthenticated}>
                  <ChatPage
                    messages={messages}
                    setMessages={setMessages}
                    clearVisibleMessages={clearVisibleMessages}
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
              path="/settings"
              element={
                <ProtectedRoute isAuthenticated={isAuthenticated}>
                  <SettingsPage token={token} />
                </ProtectedRoute>
              }
            />

            <Route
              path="/system"
              element={
                <ProtectedRoute isAuthenticated={isAuthenticated}>
                  <Navigate to="/settings" replace />
                </ProtectedRoute>
              }
            />

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
