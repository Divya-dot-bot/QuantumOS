import type {
  ExperimentRequest,
  QuantumResult,
} from "../types/quantum";

const API_BASE_URL = "https://quantumos-api.onrender.com";

export async function executeQuantumExperiment(
  request: ExperimentRequest
): Promise<QuantumResult> {
  const response = await fetch(
    `${API_BASE_URL}/api/quantum/execute`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(request),
    }
  );

  if (!response.ok) {
    let message = "Quantum execution failed.";

    try {
      const data = await response.json();

      if (data?.detail) {
        message =
          typeof data.detail === "string"
            ? data.detail
            : JSON.stringify(data.detail);
      }
    } catch {
      // Ignore invalid error response.
    }

    throw new Error(message);
  }

  return response.json();
}