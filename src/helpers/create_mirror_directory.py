import os

def create_mirror_directory(src_folder: str, dest_folder: str, entry_point: str) -> None:
    """
    Create a mirror directory of the `src_folder` at `dest_folder` with `entry_point` as the root name.
    """
    # Create destination folder if it doesn't exist
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
    
    # Iterate through the src_folder to get the directory structure
    for subdir, _, _ in os.walk(src_folder):
        # Generate the corresponding directory in the dest_folder
        dest_subdir = subdir.replace(src_folder, entry_point, 1)
        dest_path = os.path.join(dest_folder, dest_subdir)
        
        # Create the directory if it doesn't exist
        if not os.path.exists(dest_path):
            os.makedirs(dest_path)

def display_walked_paths(src_folder="src") -> None:
    for root, dirs, files in os.walk(src_folder):
        print(root)
        print(f"\t{dirs}")
        print(f"\t\t{files}")

# Example usage (note: this is a simulation; the code will not execute here)
# create_mirror_directory("path/to/src", "path/to/root", "data_models")

# Since I can't execute file operations, you can copy this function and run it in your local environment.
if __name__ == "__main__":
    display_walked_paths()
    #create_mirror_directory("src", "./", "tests")
    
    