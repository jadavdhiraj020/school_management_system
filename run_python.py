import os
import shutil

def delete_migrations():
    for root, dirs, files in os.walk("."):
        if "migrations" in dirs:
            migrations_dir = os.path.join(root, "migrations")
            for file in os.listdir(migrations_dir):
                if file != "__init__.py" and (file.endswith(".py") or file.endswith(".pyc")):
                    file_path = os.path.join(migrations_dir, file)
                    print(f"Deleting {file_path}")
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)

if __name__ == "__main__":
    delete_migrations()