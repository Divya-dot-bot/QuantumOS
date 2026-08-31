import "./SystemMonitor.css";

function SystemMonitor() {
  return (
    <div className="monitor-page">
      <div className="monitor-header">
        <div>
          <h1>System Monitor</h1>
          <p>Real-time QuantumOS system information</p>
        </div>

        <div className="monitor-status">
          <span className="status-dot"></span>
          SYSTEM ONLINE
        </div>
      </div>

      <div className="monitor-grid">
        {/* CPU */}
        <div className="monitor-card">
          <div className="monitor-card-header">
            <div>
              <span className="monitor-label">PROCESSOR</span>
              <h2>CPU</h2>
            </div>
            <span className="monitor-icon">⚡</span>
          </div>

          <div className="big-value">12%</div>
          <p className="value-description">Current CPU utilization</p>

          <div className="progress-track">
            <div className="progress-fill" style={{ width: "12%" }}></div>
          </div>

          <div className="monitor-details">
            <div>
              <span>Cores</span>
              <strong>4</strong>
            </div>

            <div>
              <span>Frequency</span>
              <strong>2.40 GHz</strong>
            </div>
          </div>
        </div>

        {/* Memory */}
        <div className="monitor-card">
          <div className="monitor-card-header">
            <div>
              <span className="monitor-label">MEMORY</span>
              <h2>RAM</h2>
            </div>
            <span className="monitor-icon">▣</span>
          </div>

          <div className="big-value">1.8 GB</div>
          <p className="value-description">Memory currently allocated</p>

          <div className="progress-track">
            <div className="progress-fill" style={{ width: "36%" }}></div>
          </div>

          <div className="monitor-details">
            <div>
              <span>Used</span>
              <strong>1.8 GB</strong>
            </div>

            <div>
              <span>Available</span>
              <strong>3.2 GB</strong>
            </div>
          </div>
        </div>

        {/* Quantum Engine */}
        <div className="monitor-card quantum-card">
          <div className="monitor-card-header">
            <div>
              <span className="monitor-label">QUANTUM ENGINE</span>
              <h2>Quantum Core</h2>
            </div>
            <span className="monitor-icon">Q</span>
          </div>

          <div className="big-value">8</div>
          <p className="value-description">Available qubits</p>

          <div className="monitor-details three-column">
            <div>
              <span>Active Jobs</span>
              <strong>2</strong>
            </div>

            <div>
              <span>Circuits</span>
              <strong>4</strong>
            </div>

            <div>
              <span>Completed</span>
              <strong>27</strong>
            </div>
          </div>

          <div className="engine-status">
            <span className="status-dot"></span>
            Quantum engine ready
          </div>
        </div>

        {/* System */}
        <div className="monitor-card">
          <div className="monitor-card-header">
            <div>
              <span className="monitor-label">SYSTEM</span>
              <h2>Core Services</h2>
            </div>
            <span className="monitor-icon">◈</span>
          </div>

          <div className="service-list">
            <div className="service-row">
              <span>Kernel</span>
              <strong>ACTIVE</strong>
            </div>

            <div className="service-row">
              <span>Memory Manager</span>
              <strong>ACTIVE</strong>
            </div>

            <div className="service-row">
              <span>Scheduler</span>
              <strong>ACTIVE</strong>
            </div>

            <div className="service-row">
              <span>Quantum Engine</span>
              <strong>READY</strong>
            </div>

            <div className="service-row">
              <span>Framebuffer</span>
              <strong>ACTIVE</strong>
            </div>
          </div>
        </div>
      </div>

      {/* Runtime */}
      <div className="runtime-card">
        <div>
          <span className="monitor-label">SYSTEM RUNTIME</span>
          <h2>QuantumOS Research Edition</h2>
        </div>

        <div className="runtime-stats">
          <div>
            <span>Uptime</span>
            <strong>00:14:32</strong>
          </div>

          <div>
            <span>Kernel</span>
            <strong>0.1.0</strong>
          </div>

          <div>
            <span>Architecture</span>
            <strong>x86_64</strong>
          </div>

          <div>
            <span>Boot Mode</span>
            <strong>BIOS</strong>
          </div>
        </div>
      </div>
    </div>
  );
}

export default SystemMonitor;