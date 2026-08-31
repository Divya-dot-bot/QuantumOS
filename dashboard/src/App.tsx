import {
  useState,
} from "react";

import Dashboard from "./pages/Dashboard";
import QuantumCore from "./pages/QuantumCore";
import QuantumLab from "./pages/QuantumLab";
import Processes from "./pages/Processes";
import Scheduler from "./pages/Scheduler";
import Memory from "./pages/Memory";
import Terminal from "./pages/Terminal";

import Sidebar from "./components/Sidebar";

import "./App.css";
import "./pages/QuantumLab.css";


type Page =
  | "dashboard"
  | "core"
  | "lab"
  | "processes"
  | "scheduler"
  | "memory"
  | "terminal";


function App() {
  const [page, setPage] =
    useState<Page>("dashboard");


  function renderPage() {
    switch (page) {
      case "dashboard":
        return <Dashboard />;

      case "lab":
        return <QuantumLab />;

      case "core":
        return <QuantumCore />;

      case "processes":
        return <Processes />;

      case "scheduler":
        return <Scheduler />;

      case "memory":
        return <Memory />;

      case "terminal":
        return <Terminal />;

      default:
        return <Dashboard />;
    }
  }


  return (
    <div className="app-shell">
      <Sidebar
        page={page}
        onNavigate={(nextPage) =>
          setPage(nextPage as Page)
        }
      />

      <div className="main-area">
        {renderPage()}
      </div>
    </div>
  );
}


export default App;