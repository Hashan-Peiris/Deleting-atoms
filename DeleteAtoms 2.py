
import glob

def read_poscar(file_path):
    with open(file_path, 'r', encoding="utf-8") as file:
        lines = file.readlines()

    title = lines[0].strip()
    scale_factor = float(lines[1].strip())
    lattice_vectors = [line.strip() for line in lines[2:5]]
    elements = lines[5].split()
    num_atoms = list(map(int, lines[6].split()))
    sel_dyn_enabled = lines[7].strip().lower().startswith('s')

    if sel_dyn_enabled:
        pos_start = 9
    else:
        pos_start = 8

    positions = []
    selective_flags = []

    for i in range(pos_start, pos_start + sum(num_atoms)):
        split_line = lines[i].split()
        positions.append(lines[i].strip())
        if sel_dyn_enabled:
            selective_flags.append(split_line[3:])

    return {
        'title': title,
        'scale_factor': scale_factor,
        'lattice_vectors': lattice_vectors,
        'elements': elements,
        'num_atoms': num_atoms,
        'sel_dyn_enabled': sel_dyn_enabled,
        'positions': positions,
        'selective_flags': selective_flags
    }

def write_poscar(poscar_data, file_path):
    with open(file_path, 'w') as file:
        file.write(f"{poscar_data['title']}\n")
        file.write(f"{poscar_data['scale_factor']}\n")
        for vector in poscar_data['lattice_vectors']:
            file.write(vector + "\n")

        file.write(" ".join(poscar_data['elements']) + "\n")
        file.write(" ".join(map(str, poscar_data['num_atoms'])) + "\n")

        if poscar_data['sel_dyn_enabled']:
            file.write("Selective\n")

        file.write("Direct\n")

        for i in range(len(poscar_data['positions'])):
            position_line = poscar_data['positions'][i]
            #if poscar_data['sel_dyn_enabled']:
            #    position_line += " " + " ".join(poscar_data['selective_flags'][i])
            file.write(position_line + "\n")

def delete_atoms(poscar_data, atoms_to_delete):
    atoms_to_delete = sorted(atoms_to_delete, reverse=True)
    total_atoms = sum(poscar_data['num_atoms'])

    for atom_index in atoms_to_delete:
        if atom_index < 0 or atom_index >= total_atoms:
            raise ValueError(f"Invalid atom index {atom_index}")

        poscar_data['positions'].pop(atom_index)
        if poscar_data['sel_dyn_enabled']:
            poscar_data['selective_flags'].pop(atom_index)

        atom_type = next(
            i for i, x in enumerate([sum(poscar_data['num_atoms'][:i]) for i in range(len(poscar_data['num_atoms']) + 1)]) if x > atom_index)
        poscar_data['num_atoms'][atom_type - 1] -= 1

    # Remove elements with zero atoms
    new_elements = []
    new_num_atoms = []
    for elem, num in zip(poscar_data['elements'], poscar_data['num_atoms']):
        if num > 0:
            new_elements.append(elem)
            new_num_atoms.append(num)

    poscar_data['elements'] = new_elements
    poscar_data['num_atoms'] = new_num_atoms


def main():
    pattern = 'CONTCAR_*'  # Define the pattern for input files
    atoms_to_delete = [2, 5, 7, 18]  # Specify the 0-indexed list of atoms to delete

    input_files = [file for file in glob.glob(pattern) if not file.endswith('.Deleted')]
    print ('Input files: ', input_files)

    for input_file in input_files:
        output_file = input_file + '.Deleted'

        poscar_data = read_poscar(input_file)
        delete_atoms(poscar_data, atoms_to_delete)
        write_poscar(poscar_data, output_file)

if __name__ == '__main__':
    main()

