import os
import pkg_resources
import subprocess

def get_installed_packages():
    """ Get a dictionary of installed packages and their versions. """
    installed_packages = {pkg.key: pkg.version for pkg in pkg_resources.working_set}
    return installed_packages

def extract_imports_from_file(file_path):
    """ Extract imported package names from a Python file. """
    imports = set()
    try:
        with open(file_path, 'r', encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("import "):
                    parts = line.split()
                    if len(parts) > 1:
                        imports.add(parts[1].split('.')[0])
                elif line.startswith("from "):
                    parts = line.split()
                    if len(parts) > 1:
                        imports.add(parts[1].split('.')[0])
    except Exception as e:
        print(f"Skipping {file_path} due to error: {e}")
    return imports

def find_python_files_and_extract_imports(root_directory):
    """ Recursively find Python files and extract all imports. """
    all_imports = set()
    for subdir, _, files in os.walk(root_directory):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(subdir, file)
                all_imports.update(extract_imports_from_file(file_path))
    return all_imports

def generate_requirements_txt(directory, output_file="requirements.txt"):
    """ Generate a requirements.txt file by scanning Python files for imports. """
    print(f"Scanning directory: {directory} ...")
    
    # Get all imports from Python files
    used_packages = find_python_files_and_extract_imports(directory)

    # Get installed packages and their versions
    installed_packages = get_installed_packages()

    # Prepare the requirements list
    requirements = []
    for package in sorted(used_packages):
        if package in installed_packages:
            requirements.append(f"{package}=={installed_packages[package]}")
        else:
            print(f"⚠ Warning: Package '{package}' is not installed.")

    # Write to requirements.txt
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(requirements))
    
    print(f"✅ requirements.txt has been generated successfully!")

# Run the script
if __name__ == "__main__":
    target_directory = os.getcwd()  # Change this if you want a specific directory
    generate_requirements_txt(target_directory)
