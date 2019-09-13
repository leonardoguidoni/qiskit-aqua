"""
This module implements the print of a state vector
"""

class PrintVector:

    def __init__(self, num_qubits=None, vector=None, style=None):
        """
        Args:
            vector (array): state vector
            style (string): style of vector print

        """
        self._numqubits=num_qubits
        self._vector=vector
        self._style=style
        self._dim=2**num_qubits
        #if(self._dim != len(vector) ):
        #   raise QiskitChemistryError("Number of qubits not consistent with vector size")

    def show(self):
        if(self._style == 'simple'):
            for i in range(self._dim):
                print(i,self._vector[i])
