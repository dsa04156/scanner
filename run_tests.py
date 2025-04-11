import os
import subprocess

TESTCASE_DIR = "testcases"
SOLUTION_DIR = "solutions"
MINIC_RUN_COMMAND = ["python", "MiniC.py"]  # 혹은 ["python3", "MiniC.py"] 또는 gradle 실행

def run_test(input_file, expected_file):
    print(f"🔍 Testing {input_file} ...")

    result = subprocess.run(MINIC_RUN_COMMAND + [input_file], capture_output=True, text=True)
    output = result.stdout.strip()

    with open(expected_file, "r", encoding="utf-8") as f:
        expected = f.read().strip()

    if output == expected:
        print("✅ PASS")
        return True
    else:
        print("❌ FAIL")
        print("---- Output ----")
        print(output)
        print("---- Expected ----")
        print(expected)
        return False

def main():
    for fname in os.listdir(TESTCASE_DIR):
        if fname.endswith(".txt"):
            input_path = os.path.join(TESTCASE_DIR, fname)
            expected_path = os.path.join(SOLUTION_DIR, f"s_" + fname)

            if os.path.exists(expected_path):
                test = run_test(input_path, expected_path)
                if test == False:
                    break
            else:
                print(f"⚠️  No solution for {fname}")

if __name__ == "__main__":
    main()
