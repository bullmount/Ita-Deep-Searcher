import pytest

def run_all():
    exit_code = pytest.main(["tests/", "-v"])
    if exit_code == 0:
        print("✅ Tutti i test sono passati.")
    else:
        print(f"❌ Alcuni test hanno fallito (exit code {exit_code}).")

if __name__ == "__main__":
    run_all()