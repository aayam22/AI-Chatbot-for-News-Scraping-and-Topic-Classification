import { Link, useLocation, useNavigate } from "react-router-dom";

/**
 * Sidebar Component - Navigation and layout sidebar
 * Handles menu items, collapse toggle, and logout
 */
export default function Sidebar({
  onLogout,
  isCollapsed,
  setIsCollapsed,
  isMobileOpen,
  onMobileClose,
  onNavigate,
}) {
  const location = useLocation();
  const navigate = useNavigate();

  const menuItems = [
    { name: "FEED", path: "/", icon: "[]" },
    { name: "ANALYSIS", path: "/analysis", icon: "()" },
    { name: "ARCHIVE", path: "/archive", icon: "##" },
    { name: "SETTINGS", path: "/settings", icon: "::" },
  ];

  const handleLogout = () => {
    onLogout();
    onMobileClose?.();
    navigate("/login");
  };

  return (
    <aside
      className={`fixed inset-y-0 left-0 z-40 flex h-screen flex-col overflow-hidden border-r-4 border-black bg-[#efefef]/95 shadow-[14px_0_40px_rgba(0,0,0,0.06)] backdrop-blur transition-all duration-300 ${
        isCollapsed ? "lg:w-20" : "lg:w-[16.25rem]"
      } w-[18rem] ${isMobileOpen ? "translate-x-0" : "-translate-x-full"} lg:translate-x-0`}
    >
      <div className={`relative border-b-2 border-black ${isCollapsed ? "px-3 py-6 lg:px-0" : "px-6 py-6"}`}>
        <button
          type="button"
          onClick={() => setIsCollapsed(!isCollapsed)}
          title={isCollapsed ? "Expand" : "Collapse"}
          className={`absolute top-5 hidden h-8 w-8 items-center justify-center border-2 border-black bg-white text-sm font-black transition hover:-translate-y-0.5 lg:flex ${
            isCollapsed ? "left-1/2 -translate-x-1/2" : "right-4"
          }`}
        >
          {isCollapsed ? ">>" : "<<"}
        </button>

        <button
          type="button"
          onClick={onMobileClose}
          className="absolute right-4 top-5 inline-flex h-8 w-8 items-center justify-center border-2 border-black bg-white text-sm font-black transition hover:-translate-y-0.5 lg:hidden"
        >
          X
        </button>

        {!isCollapsed ? (
          <div className="pr-10">
            <p className="intel-kicker mb-3">Monitor active</p>
            <h2 className="text-[1.35rem] font-black tracking-[-0.08em] text-zinc-950">
              INTEL_CORE
            </h2>
            <p className="mt-2 text-[11px] font-bold uppercase tracking-[0.16em] text-zinc-500">
              Status: Optimal
            </p>
          </div>
        ) : (
          <div className="hidden items-center justify-center lg:flex">
            <span className="text-xl font-black tracking-[-0.08em] text-zinc-950">I_C</span>
          </div>
        )}
      </div>

      <nav className="flex-1 space-y-1 px-3 py-4">
        {menuItems.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.name}
              to={item.path}
              onClick={onNavigate}
              className="block no-underline"
            >
              <div
                className={`flex items-center gap-3 rounded-2xl border px-4 py-4 text-sm font-black tracking-[0.12em] transition ${
                  isCollapsed ? "justify-center lg:px-0" : "justify-start"
                } ${
                  isActive
                    ? "border-black bg-zinc-950 text-white shadow-[0_14px_30px_rgba(17,17,17,0.18)]"
                    : "border-transparent text-zinc-900 hover:border-black/10 hover:bg-white/70"
                }`}
              >
                <span className="text-lg">{item.icon}</span>
                {!isCollapsed && <span>{item.name}</span>}
              </div>
            </Link>
          );
        })}
      </nav>

      <div className="border-t-2 border-black p-5">
        {!isCollapsed && (
          <div className="mb-4 rounded-2xl border border-black/10 bg-white/70 p-4">
            <p className="intel-kicker mb-2">Workspace</p>
            <p className="text-sm font-semibold leading-6 text-zinc-700">
              Chat, analytics, archive, and controls in one newsroom-style console.
            </p>
          </div>
        )}
        <button
          type="button"
          onClick={handleLogout}
          className="intel-button-secondary w-full gap-2 border-black/20 bg-white"
        >
          <span>{"<-"}</span> {!isCollapsed && "LOGOUT"}
        </button>
      </div>
    </aside>
  );
}
