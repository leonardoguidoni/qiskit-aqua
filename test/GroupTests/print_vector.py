
import numpy 
from qiskit.aqua.utils import PrintVector

num_qubits = 4
vector = numpy.zeros(2**num_qubits)
stampa = PrintVector(vector=vector,num_qubits=num_qubits,style='simple')
stampa.show()
