import { useState } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import NewsTerminal from "./components/NewsChat"; // updated name

function App() {
  const [messages, setMessages] = useState([]); // persist chat

  return (
    <BrowserRouter>
      <div style={{ display: "flex", minHeight: "100vh" }}>
        
        {/* Sidebar */}
        <Sidebar />

        {/* Main content */}
        <div style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "auto" }}>
          <Routes>
            <Route
              path="/"
              element={<NewsTerminal messages={messages} setMessages={setMessages} />}
            />
            <Route path="/analysis" element={<h1>Analysis Page</h1>} />
            <Route path="/archive" element={<h1>Archive Page</h1>} />
            <Route path="/system" element={<h1>System Page</h1>} />
          </Routes>
        </div>

      </div>
    </BrowserRouter>
  );
}

export default App;