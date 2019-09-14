from qiskit.chemistry import FermionicOperator
from qiskit.chemistry.drivers import PyQuanteDriver, PySCFDriver, UnitsType
from enum import Enum
from qiskit import visualization

import numpy
import logging
from qiskit.chemistry import set_qiskit_chemistry_logging
set_qiskit_chemistry_logging(logging.INFO)

DRIVER = 'PySCF'
MOLECULE = 'HeH+'
DISTANCE = 1.2
CONSTRAINT = 1.0
INITIAL_POINT = 'random' 


class BasisType(Enum):
    BSTO3G = 'sto3g'
    B631G = '6-31g'
    B631GSS = '6-31g**'

if(DRIVER == 'PySCF'):
    if(MOLECULE == 'H2sto3g'):
        driver = PySCFDriver(atom='H .0 .0 .0; H .0 .0 0.735', unit=UnitsType.ANGSTROM, basis='sto3g')
    if(MOLECULE == 'HeH+'):
        driver = PySCFDriver(atom='He .0 .0 .0; H .0 .0 '+ str(DISTANCE) +' ', unit=UnitsType.ANGSTROM,charge=1,spin=0,basis='6-31g')

if(DRIVER == 'PyQuante'):
    if(MOLECULE == 'H2sto3g'):
        driver = PyQuanteDriver(atoms='H .0 .0 .0; H .0 .0 0.735',charge=0,spin=0,basis='sto3g')
    if(MOLECULE == 'HeH+'):
        driver = PyQuanteDriver(atoms='He .0 .0 .0; H .0 .0 '+ str(DISTANCE) +' ', charge=1,multiplicity=1,basis=BasisType.B631G)
#driver = PyQuanteDriver(atoms='H .0 .0 .0; H .0 .0 0.735', basis=BasisType.BSTO3G)

molecule = driver.run()
num_particles = molecule.num_alpha + molecule.num_beta
num_spin_orbitals = molecule.num_orbitals * 2

# Build the qubit operator, which is the input to the VQE algorithm in Aqua
part_cons_parm=CONSTRAINT
ferOp = FermionicOperator(h1=molecule.one_body_integrals, h2=molecule.two_body_integrals, part_cons_parm=part_cons_parm, num_particles=num_particles)
map_type = 'jordan_wigner'
qubitOp = ferOp.mapping(map_type)
#qubitOp = qubitOp.two_qubit_reduced_operator(num_particles)
num_qubits = qubitOp.num_qubits

# set the backend for the quantum computation
from qiskit import Aer
backend = Aer.get_backend('statevector_simulator')

# setup a classical optimizer for VQE
from qiskit.aqua.components.optimizers import L_BFGS_B
optimizer = L_BFGS_B(maxfun=10000,maxiter=150000)

# setup the initial state for the variational form
from qiskit.chemistry.aqua_extensions.components.initial_states import HartreeFock
init_state = HartreeFock(num_qubits, num_spin_orbitals, num_particles,two_qubit_reduction=False,qubit_mapping=map_type)

# setup the variational form for VQE
from qiskit.aqua.components.variational_forms import RYRZ
var_form = RYRZ(num_qubits, initial_state=init_state, depth=2)
if (INITIAL_POINT == 'random'):
    initial_point = None
if (INITIAL_POINT == 'HF'):
    initial_point = numpy.zeros(var_form.num_parameters)

# setup and run VQE
from qiskit.aqua.algorithms import VQE
algorithm = VQE(qubitOp, var_form, optimizer,initial_point=initial_point)
result = algorithm.run(backend)
print("ENERGY =",result['energy'],"WITH CONSTRAINT =",part_cons_parm)
min_vector=result['min_vector']
print('min_vector = ',min_vector)
graph = visualization.plot_state_hinton(min_vector,title='eigenstate',figsize=None)
graph.show()

opt_params=result['opt_params']
ferOp = FermionicOperator(h1=molecule.one_body_integrals, h2=molecule.two_body_integrals,part_cons_parm=None)
map_type = 'jordan_wigner'
qubitOp = ferOp.mapping(map_type)
#from qiskit.aqua.components.optimizers import SPSA
from qiskit.chemistry import EnergyEvaluation
from qiskit.aqua import QuantumInstance
quantum_instance = QuantumInstance(backend) 
energy_evaluation=EnergyEvaluation(qubitOp, var_form,parameters=opt_params,quantum_instance=quantum_instance,use_simulator_operator_mode = True)
print("ENERGY =",energy_evaluation._energy_evaluation(opt_params),"WITHOUT THE CONSTRAINT")
#optimizer = SPSA(max_trials=1)
#algorithm = VQE(qubitOp, var_form, optimizer,initial_point=opt_params)
#algorithm._quantum_instance=quantum_instance
#energy_without_const=algorithm._energy_evaluation(opt_params) 
#result = algorithm.run(backend)
#print(result['energy'])
#print(energy_without_const)
