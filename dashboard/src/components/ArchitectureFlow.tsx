/**
 * QuantumOS Dashboard
 *
 * Visual representation of the QuantumOS execution pipeline.
 */

interface ArchitectureNode {
  name: string;
  description: string;
}


interface ArchitectureFlowProps {
  nodes?: ArchitectureNode[];
}


const DEFAULT_NODES: ArchitectureNode[] = [
  {
    name: "API",
    description: "HTTP Interface",
  },
  {
    name: "Compiler",
    description: "Circuit Processing",
  },
  {
    name: "Scheduler",
    description: "Job Management",
  },
  {
    name: "Runtime",
    description: "Execution Engine",
  },
  {
    name: "QVM",
    description: "Quantum Backend",
  },
];


function ArchitectureFlow({
  nodes = DEFAULT_NODES,
}: ArchitectureFlowProps) {
  return (
    <section className="architecture">

      <div className="architecture-header">

        <span className="panel-kicker">
          SYSTEM ARCHITECTURE
        </span>

        <h2>
          QuantumOS Execution Pipeline
        </h2>

        <p>
          Quantum workloads move through the
          platform from submission to execution.
        </p>

      </div>


      <div
        className="architecture-flow"
        aria-label="QuantumOS execution pipeline"
      >

        {nodes.map(
          (node, index) => (
            <div
              className="architecture-step"
              key={`${node.name}-${index}`}
            >

              <div className="architecture-node">

                <span className="architecture-index">
                  {String(index + 1).padStart(2, "0")}
                </span>

                <strong>
                  {node.name}
                </strong>

                <small>
                  {node.description}
                </small>

              </div>


              {index < nodes.length - 1 && (
                <span
                  className="architecture-arrow"
                  aria-hidden="true"
                >
                  →
                </span>
              )}

            </div>
          ),
        )}

      </div>

    </section>
  );
}


export default ArchitectureFlow;