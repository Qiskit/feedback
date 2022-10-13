# Step 1: setup

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

backend = AerSimulator(method="statevector")



# Step 2: conditional initialisation

qc = QuantumCircuit(1, 2)
qc.h(0)  # This is just a stand-in for more complex real-world setup.
qc.measure(0, 0)

# Unlike c_if, we can have more than one instruction in the block, and it only
# requires a single evaluation of the condition.  That's especially important if
# the bit is written to part way through the block.
with qc.if_test((0, True)):
    qc.reset(0)
    qc.x(0)
qc.measure(0, 1)

qc.draw()
backend.run(qc).result().get_counts()  # {'00': 0.5, '11': 0.5}



# Step 3: repeat until success.

# Previously this wasn't representable in Qiskit at all, because we didn't have
# any concept of a run-time loop.

qc = QuantumCircuit(1, 2)
qc.h(0)
qc.measure(0, 0)
with qc.while_loop((0, False)):
    qc.reset(0)
    qc.h(0)
    qc.measure(0, 0)
qc.measure(0, 1)

qc.draw()
backend.run(qc).result().get_counts()  # {'11': 1}



# Step 4: repeat until success, with limits on the number of iterations.

qc = QuantumCircuit(1, 2)
with qc.for_loop(range(2)):
    qc.reset(0)
    qc.h(0)
    qc.measure(0, 0)
    with qc.if_test((0, True)):
        # 'break' (and 'continue') is also supported by Aer, but won't be part
        # of the initial transpiler support for swap routing.
        qc.break_loop()
qc.measure(0, 1)
backend.run(qc).result().get_counts()  # {'00': 0.25, '11': 0.75}



# Step 5: converting old-style c_if to IfElseOp.

# This transpiler pass is available in Terra 0.22 for backends to use in their
# injected pass-manager stages, so they can begin transitioning to the new forms
# immediately, and can start deprecating support for handling old-style
# `condition`.
from qiskit.transpiler.passes import ConvertConditionsToIfOps

qc = QuantumCircuit(1, 1)
qc.h(0)
qc.measure(0, 0)
qc.x(0).c_if(0, False)
qc.draw()

pass_ = ConvertConditionsToIfOps()
pass_(qc).draw()



# Other things mentioned:
#
# - The `QuantumCircuit.for_loop` context manager returns a `Parameter` object
#   that can be used in angle expressions in the loop body's gates.  The
#   OpenQASM 3 exporter understands this.
#
# - The `QuantumCircuit.if_test` context manager returns a context-manager
#   object that can be entered immediately on termination of the "true" body, to
#   make an "else" body.  For example:
#
#       with qc.if_test((0, False)) as else_:
#           qc.x(0)
#       with else_:
#           qc.z(0)
#
# - The OpenQASM 3 exporter supports all these constructs.  The easiest path to
#   access that is `qiskit.qasm3.dumps`.
