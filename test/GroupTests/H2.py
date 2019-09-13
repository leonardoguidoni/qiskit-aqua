from qiskit.chemistry import FermionicOperator
from qiskit.chemistry.drivers import PySCFDriver, UnitsType

# Use PySCF, a classical computational chemistry software package, to compute the one-body and two-body integrals in
# molecular-orbital basis, necessary to form the Fermionic operator
driver = PySCFDriver(atom='H .0 .0 .0; H .0 .0 0.735',
                    unit=UnitsType.ANGSTROM,
                    basis='sto3g')
#                    basis='6-31g')
molecule = driver.run()
num_particles = molecule.num_alpha + molecule.num_beta
num_spin_orbitals = molecule.num_orbitals * 2

# Build the qubit operator, which is the input to the VQE algorithm in Aqua
ferOp = FermionicOperator(h1=molecule.one_body_integrals, h2=molecule.two_body_integrals, part_cons_parm=0.0, num_particles=num_particles)
map_type = 'PARITY'
qubitOp = ferOp.mapping(map_type)
qubitOp = qubitOp.two_qubit_reduced_operator(num_particles)
num_qubits = qubitOp.num_qubits
for pauli in qubitOp.paulis:
   print (pauli[0],str(pauli[1]))

# set the backend for the quantum computation
from qiskit import Aer
backend = Aer.get_backend('statevector_simulator')

# setup a classical optimizer for VQE
from qiskit.aqua.components.optimizers import L_BFGS_B
optimizer = L_BFGS_B()

# setup the initial state for the variational form
from qiskit.chemistry.aqua_extensions.components.initial_states import HartreeFock
init_state = HartreeFock(num_qubits, num_spin_orbitals, num_particles)

# setup the variational form for VQE
from qiskit.aqua.components.variational_forms import RYRZ
var_form = RYRZ(num_qubits, initial_state=init_state)

# setup and run VQE
from qiskit.aqua.algorithms import VQE
algorithm = VQE(qubitOp, var_form, optimizer)
result = algorithm.run(backend)
print('OPTIMISED IN ',result['num_optimizer_evals'],' STEPS')
min_vector=result['min_vector']
from qiskit.visualization import plot_state_city
fig=plot_state_city(min_vector)
fig.show()
print(result['energy'])
