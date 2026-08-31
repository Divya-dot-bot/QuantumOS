import type { FC } from "react";

export type Page =
  | "dashboard"
  | "core"
  | "lab"
  | "processes"
  | "scheduler"
  | "memory"
  | "terminal";

interface SidebarProps {
  page?: Page;
  onNavigate: (page: Page) => void;
}

const navigation: Array<{
  id: Page;
  label: string;
}> = [
  {
    id: "dashboard",
    label: "Dashboard",
  },
  {
    id: "core",
    label: "Quantum Core",
  },
  {
    id: "lab",
    label: "Quantum Lab",
  },
  {
    id: "processes",
    label: "Processes",
  },
  {
    id: "scheduler",
    label: "Scheduler",
  },
  {
    id: "memory",
    label: "Memory",
  },
  {
    id: "terminal",
    label: "Terminal",
  },
];

const Sidebar: FC<SidebarProps> = ({
  page,
  onNavigate,
}) => {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="brand-mark">
          Q
        </div>

        <div>
          <strong>QuantumOS</strong>
          <span>Quantum Runtime</span>
        </div>
      </div>

      <nav className="sidebar-nav">
        {navigation.map((item) => (
          <button
            type="button"
            key={item.id}
            className={
              page === item.id
                ? "nav-item active"
                : "nav-item"
            }
            onClick={() =>
              onNavigate(item.id)
            }
          >
            {item.label}
          </button>
        ))}
      </nav>
    </aside>
  );
};

export default Sidebar;