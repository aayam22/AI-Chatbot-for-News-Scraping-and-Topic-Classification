import { Link, useLocation, useNavigate } from "react-router-dom";

/**
 * Sidebar Component - Navigation and layout sidebar
 * Handles menu items, collapse toggle, and logout
 */
export default function Sidebar({ onLogout, isCollapsed, setIsCollapsed }) {
  const location = useLocation();
  const navigate = useNavigate();

  const menuItems = [
    { name: "FEED", path: "/", icon: "▤" },
    { name: "ANALYSIS", path: "/analysis", icon: "◒" },
    { name: "ARCHIVE", path: "/archive", icon: "▥" },
    { name: "SYSTEM", path: "/system", icon: "⚙" },
  ];

  const sidebarStyle = {
    width: isCollapsed ? '80px' : '260px',
    height: '100vh',
    flexShrink: 0,
    borderRight: '4px solid #000',
    backgroundColor: '#eee',
    display: 'flex',
    flexDirection: 'column',
    transition: 'width 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
    fontFamily: '"Space Grotesk", sans-serif',
    overflow: 'hidden',
    position: 'fixed',
    top: 0,
    left: 0,
    zIndex: 1000
  };

  const headerStyle = {
    padding: isCollapsed ? '24px 0' : '24px',
    borderBottom: '2px solid #000',
    display: 'flex',
    flexDirection: 'column',
    alignItems: isCollapsed ? 'center' : 'flex-start',
    minHeight: '100px'
  };

  const toggleButtonStyle = {
    position: 'absolute',
    top: '24px',
    right: isCollapsed ? 'calc(50% - 12px)' : '16px',
    background: 'none',
    border: '2px solid #000',
    cursor: 'pointer',
    fontWeight: '900',
    width: '24px',
    height: '24px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#fff',
    zIndex: 10
  };

  const handleLogout = () => {
    onLogout();
    navigate("/login");
  };

  return (
    <aside style={sidebarStyle}>
      {/* Toggle Button */}
      <button 
        onClick={() => setIsCollapsed(!isCollapsed)} 
        style={toggleButtonStyle}
        title={isCollapsed ? "Expand" : "Collapse"}
      >
        {isCollapsed ? '»' : '«'}
      </button>

      {/* Header */}
      <div style={headerStyle}>
        {!isCollapsed ? (
          <>
            <h2 style={{ 
              fontSize: '20px', 
              fontWeight: '900', 
              margin: 0, 
              letterSpacing: '-1px' 
            }}>
              INTEL_CORE
            </h2>
            <div style={{ 
              fontSize: '10px', 
              fontWeight: 'bold', 
              opacity: 0.6, 
              marginTop: '4px' 
            }}>
              STATUS: OPTIMAL
            </div>
          </>
        ) : (
          <div style={{ fontWeight: '900', fontSize: '20px' }}>I_C</div>
        )}
      </div>

      {/* Navigation */}
      <nav style={{ flex: 1, padding: '12px 0' }}>
        {menuItems.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.name}
              to={item.path}
              style={{ textDecoration: 'none', color: isActive ? '#fff' : '#000' }}
            >
              <div style={{
                padding: isCollapsed ? '16px 0' : '16px 24px',
                fontWeight: '900',
                fontSize: '14px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: isCollapsed ? 'center' : 'flex-start',
                gap: '12px',
                backgroundColor: isActive ? '#000' : 'transparent',
                borderBottom: '1px solid rgba(0,0,0,0.1)',
                transition: 'all 0.2s'
              }}>
                <span style={{ fontSize: '20px' }}>{item.icon}</span>
                {!isCollapsed && <span>{item.name}</span>}
              </div>
            </Link>
          );
        })}
      </nav>

      {/* Footer - Logout Button */}
      <div style={{ padding: '24px', borderTop: '2px solid #000' }}>
        <button 
          onClick={handleLogout} 
          style={{
            width: '100%',
            padding: '12px',
            backgroundColor: 'transparent',
            border: '2px solid #000',
            fontWeight: '900',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px',
            boxShadow: '4px 4px 0px #000',
            transform: 'translate(-2px, -2px)',
          }}
        >
          <span>↩</span> {!isCollapsed && 'LOGOUT'}
        </button>
      </div>
    </aside>
  );
}
