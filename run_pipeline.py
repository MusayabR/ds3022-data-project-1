import subprocess
import sys


def main():
    """Run each stage in order, stop if one fails."""
    for script in ["load.py", "clean.py", "transform.py", "analysis.py"]:
        print(f"--- running {script} ---")
        subprocess.run([sys.executable, script], check=True)


if __name__ == "__main__":
    main()
