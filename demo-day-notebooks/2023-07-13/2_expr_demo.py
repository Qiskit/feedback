# Cell 1: simple representation

from qiskit import QuantumCircuit
from qiskit.circuit import QuantumRegister, ClassicalRegister, Clbit
from qiskit.circuit.classical import expr

cr1 = ClassicalRegister(3, "cr1")
cr2 = ClassicalRegister(3, "cr2")

expr.equal(expr.bit_and(cr1, cr2), 5)


# Cell 2: where can I use these?

qc1 = QuantumCircuit(QuantumRegister(3), cr1, cr2)

with qc1.if_test((cr1, 5)):
    qc1.x(0)

with qc1.if_test(expr.equal(cr1, 5)):
    qc1.x(0)

# But we're not limited to equality relations!

with qc1.if_test(expr.less_equal(cr1, 5)):
    qc1.z(0)

qc1.data[-1].operation.condition



# Cell 3: where else?

qc2 = QuantumCircuit(QuantumRegister(3), cr1, cr2)
with qc2.while_loop(expr.logic_or(expr.equal(cr1, 5), cr2[0])):
    qc2.x(0)

with qc2.switch(expr.bit_and(cr1, cr2)) as case:
    with case(0):
        qc2.x(0)
    with case(1):
        qc2.z(0)
    with case(2):
        qc2.x(1)
    with case(case.DEFAULT):
        qc2.z(1)



# Cell 4: integration testing

import io
from qiskit import transpile, qasm3, qpy
from qiskit_aer import AerSimulator

backend = AerSimulator(method="statevector")

transpiled = transpile(qc1, backend)
with io.BytesIO() as fptr:
    qpy.dump(transpiled, fptr)
    fptr.seek(0)
    loaded = qpy.load(fptr)[0]

print(qasm3.dumps(loaded))
