import { useState } from "react";

import {
  getBackends,
  getHealth,
  getJobs,
} from "../services/api";

interface TerminalLine {
  type: "input" | "output" | "error";
  text: string;
}

const HELP_TEXT = [
  "Available QuantumOS commands:",
  "",
  "help       Show this help message",
  "status     Show API health status",
  "backends   List registered quantum backends",
  "jobs       List current quantum jobs",
  "clear      Clear the terminal",
];

export default function Terminal() {
  const [command, setCommand] =
    useState("");

  const [lines, setLines] =
    useState<TerminalLine[]>([
      {
        type: "output",
        text:
          "QuantumOS Terminal v0.1.0",
      },
      {
        type: "output",
        text:
          'Type "help" to see available commands.',
      },
    ]);

  const [running, setRunning] =
    useState(false);

  async function executeCommand() {
    const value =
      command.trim().toLowerCase();

    if (!value) {
      return;
    }

    setLines((current) => [
      ...current,
      {
        type: "input",
        text: `$ ${value}`,
      },
    ]);

    setCommand("");

    if (value === "clear") {
      setLines([]);
      return;
    }

    if (value === "help") {
      setLines((current) => [
        ...current,
        ...HELP_TEXT.map((text) => ({
          type: "output" as const,
          text,
        })),
      ]);

      return;
    }

    try {
      setRunning(true);

      if (value === "status") {
        const health =
          await getHealth();

        setLines((current) => [
          ...current,
          {
            type: "output",
            text: `Service: ${health.service}`,
          },
          {
            type: "output",
            text: `Status: ${health.status}`,
          },
          {
            type: "output",
            text: `Version: ${health.version}`,
          },
        ]);

        return;
      }

      if (value === "backends") {
        const response =
          await getBackends();

        const output =
          response.backends.map(
            (backend) =>
              `${backend.backend_id} | ${backend.name} | ${backend.num_qubits} qubits | ${backend.status}`,
          );

        setLines((current) => [
          ...current,
          {
            type: "output",
            text:
              output.length > 0
                ? output.join("\n")
                : "No backends registered.",
          },
        ]);

        return;
      }

      if (value === "jobs") {
        const jobs =
          await getJobs();

        const output = jobs.map(
          (job) =>
            `${job.job_id} | ${job.status} | ${job.shots} shots | priority ${job.priority}`,
        );

        setLines((current) => [
          ...current,
          {
            type: "output",
            text:
              output.length > 0
                ? output.join("\n")
                : "No jobs found.",
          },
        ]);

        return;
      }

      setLines((current) => [
        ...current,
        {
          type: "error",
          text:
            `Unknown command: ${value}. Type "help".`,
        },
      ]);
    } catch (err) {
      setLines((current) => [
        ...current,
        {
          type: "error",
          text:
            err instanceof Error
              ? err.message
              : "Command failed.",
        },
      ]);
    } finally {
      setRunning(false);
    }
  }

  function handleKeyDown(
    event: React.KeyboardEvent<HTMLInputElement>,
  ) {
    if (event.key === "Enter") {
      void executeCommand();
    }
  }

  return (
    <main className="dashboard-page">
      <section className="page-header">
        <div>
          <span className="page-kicker">
            QUANTUMOS SHELL
          </span>

          <h1>Terminal</h1>

          <p>
            Controlled interface for inspecting
            the local QuantumOS runtime.
          </p>
        </div>
      </section>

      <section className="panel">
        <div className="panel-header">
          <div>
            <span className="panel-kicker">
              LOCAL RUNTIME
            </span>

            <h2>QuantumOS Console</h2>
          </div>
        </div>

        <div
          style={{
            background:
              "rgba(0, 0, 0, 0.25)",
            padding: "20px",
            borderRadius: "12px",
            fontFamily:
              "ui-monospace, SFMono-Regular, Consolas, monospace",
            whiteSpace: "pre-wrap",
            minHeight: "280px",
          }}
        >
          {lines.map(
            (line, index) => (
              <div
                key={`${index}-${line.text}`}
                style={{
                  marginBottom: "8px",
                }}
              >
                {line.text}
              </div>
            ),
          )}

          <div
            style={{
              display: "flex",
              gap: "8px",
              marginTop: "16px",
            }}
          >
            <span>$</span>

            <input
              value={command}
              onChange={(event) =>
                setCommand(
                  event.target.value,
                )
              }
              onKeyDown={
                handleKeyDown
              }
              disabled={running}
              placeholder="type a command..."
              style={{
                flex: 1,
                background: "transparent",
                border: "none",
                outline: "none",
                color: "inherit",
                font: "inherit",
              }}
            />
          </div>
        </div>
      </section>

      <section className="architecture">
        <span className="panel-kicker">
          SECURITY
        </span>

        <h2>
          Browser commands are intentionally
          restricted.
        </h2>

        <p>
          The terminal currently exposes only
          predefined QuantumOS API operations.
          Arbitrary operating-system commands are
          not executed from the browser.
        </p>
      </section>
    </main>
  );
}