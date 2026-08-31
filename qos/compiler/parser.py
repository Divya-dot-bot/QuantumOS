"""
QuantumOS Compiler - Parser

Parses a small human-readable quantum program format into
QuantumCircuit objects.

Example program:

    qubits 2
    h 0
    cx 0 1
    measure
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from qos.core.circuit import QuantumCircuit


@dataclass(frozen=True)
class ParsedInstruction:
    """Represents one parsed quantum instruction."""

    operation: str
    operands: tuple[int, ...] = ()


class QuantumProgramParser:
    """
    Parser for the QuantumOS MVP quantum program format.

    Supported instructions:

        qubits N
        i Q
        x Q
        y Q
        z Q
        h Q
        s Q
        t Q
        cx CONTROL TARGET
        measure

    Comments begin with '#'.
    Blank lines are ignored.
    """

    SINGLE_QUBIT_GATES = {
        "i",
        "x",
        "y",
        "z",
        "h",
        "s",
        "t",
    }

    TWO_QUBIT_GATES = {
        "cx",
    }

    def parse(
        self,
        source: str,
    ) -> QuantumCircuit:
        """
        Parse a complete quantum program.

        Args:
            source: QuantumOS program text.

        Returns:
            A QuantumCircuit containing the parsed operations.

        Raises:
            TypeError: If source is not a string.
            ValueError: If the program is invalid.
        """

        if not isinstance(source, str):
            raise TypeError("source must be a string")

        instructions = self._parse_instructions(source)

        if not instructions:
            raise ValueError(
                "quantum program cannot be empty"
            )

        num_qubits = self._extract_qubit_count(instructions)

        circuit = QuantumCircuit(num_qubits)

        for instruction in instructions:
            self._apply_instruction(
                circuit,
                instruction,
            )

        return circuit

    def parse_lines(
        self,
        lines: Iterable[str],
    ) -> QuantumCircuit:
        """
        Parse an iterable of source lines.
        """

        if isinstance(lines, str):
            return self.parse(lines)

        return self.parse(
            "\n".join(lines)
        )

    def _parse_instructions(
        self,
        source: str,
    ) -> list[ParsedInstruction]:
        """Convert source text into parsed instructions."""

        instructions: list[ParsedInstruction] = []

        for line_number, raw_line in enumerate(
            source.splitlines(),
            start=1,
        ):
            line = raw_line.split("#", 1)[0].strip()

            if not line:
                continue

            tokens = line.split()

            operation = tokens[0].lower()

            if operation == "qubits":
                operands = self._parse_operands(
                    tokens[1:],
                    line_number,
                    expected=1,
                )

                instructions.append(
                    ParsedInstruction(
                        operation="qubits",
                        operands=operands,
                    )
                )

                continue

            if operation == "measure":
                if len(tokens) != 1:
                    raise ValueError(
                        self._error(
                            line_number,
                            "measure does not accept operands",
                        )
                    )

                instructions.append(
                    ParsedInstruction(
                        operation="measure"
                    )
                )

                continue

            if operation in self.SINGLE_QUBIT_GATES:
                operands = self._parse_operands(
                    tokens[1:],
                    line_number,
                    expected=1,
                )

                instructions.append(
                    ParsedInstruction(
                        operation=operation,
                        operands=operands,
                    )
                )

                continue

            if operation in self.TWO_QUBIT_GATES:
                operands = self._parse_operands(
                    tokens[1:],
                    line_number,
                    expected=2,
                )

                instructions.append(
                    ParsedInstruction(
                        operation=operation,
                        operands=operands,
                    )
                )

                continue

            raise ValueError(
                self._error(
                    line_number,
                    f"unknown operation '{operation}'",
                )
            )

        return instructions

    def _extract_qubit_count(
        self,
        instructions: list[ParsedInstruction],
    ) -> int:
        """Extract and validate the program's qubit declaration."""

        declarations = [
            instruction
            for instruction in instructions
            if instruction.operation == "qubits"
        ]

        if len(declarations) == 0:
            raise ValueError(
                "program must contain a 'qubits N' declaration"
            )

        if len(declarations) > 1:
            raise ValueError(
                "program may contain only one 'qubits' declaration"
            )

        num_qubits = declarations[0].operands[0]

        if num_qubits < 1:
            raise ValueError(
                "number of qubits must be at least 1"
            )

        return num_qubits

    def _apply_instruction(
        self,
        circuit: QuantumCircuit,
        instruction: ParsedInstruction,
    ) -> None:
        """Apply a parsed instruction to a circuit."""

        operation = instruction.operation
        operands = instruction.operands

        if operation == "qubits":
            return

        if operation == "measure":
            # Measurement is intentionally not represented as a
            # circuit gate in the current MVP. The QVM performs
            # measurement when shots are requested.
            return

        if operation == "i":
            circuit.i(operands[0])
            return

        if operation == "x":
            circuit.x(operands[0])
            return

        if operation == "y":
            circuit.y(operands[0])
            return

        if operation == "z":
            circuit.z(operands[0])
            return

        if operation == "h":
            circuit.h(operands[0])
            return

        if operation == "s":
            circuit.s(operands[0])
            return

        if operation == "t":
            circuit.t(operands[0])
            return

        if operation == "cx":
            circuit.cx(
                operands[0],
                operands[1],
            )
            return

        raise ValueError(
            f"unsupported operation: {operation}"
        )

    @staticmethod
    def _parse_operands(
        tokens: list[str],
        line_number: int,
        expected: int,
    ) -> tuple[int, ...]:
        """Parse integer qubit operands."""

        if len(tokens) != expected:
            raise ValueError(
                QuantumProgramParser._error(
                    line_number,
                    (
                        f"expected {expected} operand(s), "
                        f"got {len(tokens)}"
                    ),
                )
            )

        operands: list[int] = []

        for token in tokens:
            try:
                value = int(token)
            except ValueError as exc:
                raise ValueError(
                    QuantumProgramParser._error(
                        line_number,
                        f"invalid qubit index '{token}'",
                    )
                ) from exc

            operands.append(value)

        return tuple(operands)

    @staticmethod
    def _error(
        line_number: int,
        message: str,
    ) -> str:
        """Create a consistent parser error message."""

        return f"line {line_number}: {message}"


def parse_program(
    source: str,
) -> QuantumCircuit:
    """
    Convenience function for parsing a QuantumOS program.

    Example:

        circuit = parse_program(
            '''
            qubits 2
            h 0
            cx 0 1
            '''
        )
    """

    parser = QuantumProgramParser()

    return parser.parse(source)


def parse(
    source: str,
) -> QuantumCircuit:
    """Convenience alias for parsing a QuantumOS program."""
    return parse_program(source)