
import logging
import functools

import numpy as np


logger = logging.getLogger(__name__)
from qiskit.aqua import set_qiskit_aqua_logging

set_qiskit_aqua_logging(0)

class EnergyEvaluation:
    """
    The Variational Quantum Eigensolver algorithm.

    See https://arxiv.org/abs/1304.3061
    """

    def __init__(self, operator, var_form, parameters, quantum_instance, operator_mode='matrix',
                 initial_point=None, aux_operators=None, use_simulator_operator_mode = False):
        """
        Constructor
        :param var_form: pass here the var form UCCSD class object, initialised (avoid to reinitialise)
        :param parameters: np.array, VQE parameters for the excitations
                        (doubling of them will happen inside this function)
        :param operator: qubit_operator object, molecular hamiltonian for example
                        (algo_input = Hamiltonian(...).run(self.qmolecule) ; qubit_op = algo_input[0]
        """

        # Gradient necessary parameters

        # self.validate(locals())
        self._var_form = var_form
        self._parameters = parameters
        self._operator = operator

        # borrowed from VQE to make a function evaluation

        # self._optimizer.set_max_evals_grouped(max_evals_grouped)
        # self._callback = callback
        if initial_point is None:
            self._initial_point = var_form.preferred_init_points
        # self._operator = operator
        self._operator_mode = operator_mode
        self._use_simulator_operator_mode = use_simulator_operator_mode
        self._eval_count = 0
        self._quantum_instance = quantum_instance
        if aux_operators is None:
            self._aux_operators = []
        else:
            self._aux_operators = [aux_operators] if not isinstance(aux_operators, list) else aux_operators
        # logger.info(self.print_settings())

    # same as in VQE.py, this will evaluate the UCCSD circuit

    def construct_circuit(self, parameter, backend=None, use_simulator_operator_mode=False):

        """Generate the circuits.

        Args:
            parameters (numpy.ndarray): parameters for variational form.
            backend (qiskit.BaseBackend): backend object.
            use_simulator_operator_mode (bool): is backend from AerProvider, if True and mode is paulis,
                           single circuit is generated.

        Returns:
            [QuantumCircuit]: the generated circuits with Hamiltonian.
        """
        input_circuit = self._var_form.construct_circuit(parameter)
        if backend is None:
            warning_msg = "Circuits used in VQE depends on the backend type, "
            from qiskit import BasicAer
            if self._operator_mode == 'matrix':
                temp_backend_name = 'statevector_simulator'
            else:
                temp_backend_name = 'qasm_simulator'
            backend = BasicAer.get_backend(temp_backend_name)
            warning_msg += "since operator_mode is '{}', '{}' backend is used.".format(
                self._operator_mode, temp_backend_name)
            logger.warning(warning_msg)
        circuit = self._operator.construct_evaluation_circuit(self._operator_mode, input_circuit, backend,
                                                              use_simulator_operator_mode=self._use_simulator_operator_mode)
        return circuit

    # This is the objective function to be passed to the optimizer that is uses for evaluation

    def _energy_evaluation(self, parameters):
        """
        Evaluate energy at given parameters for the variational form.

        Args:
            parameters (numpy.ndarray): parameters for variational form.

        Returns:
            float or list of float: energy of the hamiltonian of each parameter.
        """
        num_parameter_sets = len(parameters) // self._var_form.num_parameters
        circuits = []
        parameter_sets = np.split(parameters, num_parameter_sets)
        mean_energy = []
        std_energy = []

        for idx in range(len(parameter_sets)):
            parameter = parameter_sets[idx]
            circuit = self.construct_circuit(parameter, self._quantum_instance.backend,
                                             self._use_simulator_operator_mode)
            circuits.append(circuit)

        to_be_simulated_circuits = functools.reduce(lambda x, y: x + y, circuits)
        if self._use_simulator_operator_mode:
            extra_args = {'expectation': {
                'params': [self._operator.aer_paulis],
                'num_qubits': self._operator.num_qubits}
            }
        else:
            extra_args = {}
        result = self._quantum_instance.execute(to_be_simulated_circuits, **extra_args)

        for idx in range(len(parameter_sets)):
            # the energy
            mean, std = self._operator.evaluate_with_result(
                self._operator_mode, circuits[idx], self._quantum_instance.backend, result,
                self._use_simulator_operator_mode)
            mean_energy.append(np.real(mean))
            std_energy.append(np.real(std))
            self._eval_count += 1
            # if self._callback is not None:
            #     self._callback(self._eval_count, parameter_sets[idx], np.real(mean), np.real(std))
            logger.info('Energy evaluation {} returned {}'.format(self._eval_count, np.real(mean)))

        return mean_energy if len(mean_energy) > 1 else mean_energy[0]

