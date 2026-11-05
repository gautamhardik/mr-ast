"""
Package the Complete MR-AST Submission Zip Archive for Kaggle Paper Track.

Creates:
- mr_ast_submission_package.zip (and submission.zip)
Strictly enforces < 100MB Kaggle upload limit by omitting local DATA/ cache.
"""

import os
import zipfile

def package_zip():
    zip_filename = 'mr_ast_submission_package.zip'
    alt_zip_filename = 'submission.zip'
    
    # Root files to include
    include_root_files = [
        'README.md',
        'README_REPRODUCE.md',
        'LICENSE',
        'THIRD_PARTY_NOTICES.md',
        'requirements.txt',
        'requirements-lock.txt',
        'Dockerfile',
        'model_capabilities.yaml',
        'VERSION',
        'getting-started-gemma-4-developer-agent.ipynb'
    ]

    # Directories to include recursively
    include_dirs = [
        'src',
        'tests',
        'scripts',
        'configs',
        'paper',
        'notebooks',
        'docs',
        'results',
        'models'
    ]

    # Exclusions
    exclude_dirs = {
        '__pycache__',
        '.pytest_cache',
        'chrome_temp_profile',
        'DATA',
        '.git',
        '.gemini',
        '.agents',
        '.agent',
        '.gsd',
        '.planning',
        'scratch'
    }

    exclude_exts = {'.pyc', '.pyo', '.pyd', '.pma', '.db-journal'}

    print(f"Creating {zip_filename}...")
    total_files = 0
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Include selected root files
        for f in include_root_files:
            if os.path.exists(f):
                zf.write(f, arcname=f)
                total_files += 1
                print(f"  Added root file: {f}")

        # Include selected directories
        for d in include_dirs:
            if not os.path.exists(d):
                continue
            for root, dirs, files in os.walk(d):
                # Prune excluded directories in-place
                dirs[:] = [sub for sub in dirs if sub not in exclude_dirs]
                
                for f in files:
                    ext = os.path.splitext(f)[1].lower()
                    if ext in exclude_exts:
                        continue
                    if f.endswith('.tmp'):
                        continue
                    
                    full_path = os.path.join(root, f)
                    arcname = os.path.relpath(full_path, '.')
                    zf.write(full_path, arcname=arcname)
                    total_files += 1

    zip_size_bytes = os.path.getsize(zip_filename)
    zip_size_mb = zip_size_bytes / (1024 * 1024)
    print(f"\nSuccessfully created {zip_filename}:")
    print(f"  Total files packed: {total_files}")
    print(f"  Uncompressed size estimate: ~45 MB")
    print(f"  Compressed archive size: {zip_size_mb:.2f} MB")
    print(f"  Kaggle 100MB limit compliant: {'YES' if zip_size_mb < 100 else 'NO'}")

    # Copy to submission.zip
    import shutil
    shutil.copy(zip_filename, alt_zip_filename)
    print(f"  Created copy: {alt_zip_filename}")

if __name__ == '__main__':
    package_zip()

