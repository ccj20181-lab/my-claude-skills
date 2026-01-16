import os
import sys
import subprocess
import argparse
import json
from datetime import datetime

def run_step(step_name, command):
    print(f"\n==========================================")
    print(f"[STEP] Executing: {step_name}")
    print(f"[CMD] {command}")
    print(f"==========================================\n")

    try:
        # Using shell=True for Windows path compatibility
        result = subprocess.run(command, check=True, shell=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Step '{step_name}' FAILED with exit code {e.returncode}")
        return False

def main():
    parser = argparse.ArgumentParser(description="XHS Topic Analyzer Pipeline")
    parser.add_argument('--file', required=True, help='Input data JSON file')
    parser.add_argument('--mode', default='finance-pro', choices=['lite', 'deep', 'finance-pro'], help='Analysis mode')
    args = parser.parse_args()

    # Calculate paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    scripts_dir = os.path.join(base_dir, 'scripts')
    data_file = os.path.abspath(args.file)

    # Load config for output path
    config_path = os.path.join(base_dir, 'config.json')
    output_base_path = "."
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                output_base_path = config.get("output_base_path", ".")
        except:
            pass

    # Create output directory: F:\选题抓取\20240101_FinancePro
    today_str = datetime.now().strftime("%Y%m%d")
    mode_suffix = "每日热点" if args.mode == "lite" else "FinancePro"
    output_dir = os.path.join(output_base_path, f"{today_str}_{mode_suffix}")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    print(f"[INFO] Output Directory: {output_dir}")

    # 1. Validation
    cmd_validate = f'python "{os.path.join(scripts_dir, "validator.py")}" "{data_file}"'
    if not run_step("Data Validation", cmd_validate):
        sys.exit(1)

    # 2. Generate Image Report (NEW!)
    image_file = os.path.join(output_dir, "daily_report.png")
    cmd_image = f'python "{os.path.join(scripts_dir, "report_image.py")}" "{data_file}" "{image_file}" --mode {args.mode}'
    if not run_step("Image Report Generation", cmd_image):
        sys.exit(1)

    # 3. Push Image to WeChat (MANDATORY - CANNOT SKIP!)
    if os.path.exists(image_file):
        cmd_push = f'python "{os.path.join(scripts_dir, "push_image.py")}" --file "{image_file}" --mode {args.mode}'
        push_success = run_step("WeChat Push (Image Format)", cmd_push)
        if not push_success:
            print("\n" + "="*50)
            print("[CRITICAL ERROR] WeChat push FAILED!")
            print("Please check:")
            print("  1. PushPlus token is valid")
            print("  2. Network connection is available")
            print("  3. Image file was generated correctly")
            print("="*50)
            sys.exit(1)
        else:
            print("\n[SUCCESS] WeChat push completed!")
    else:
        print(f"\n[CRITICAL ERROR] Image file not found: {image_file}")
        sys.exit(1)

    print("\n" + "="*50)
    print("[SUCCESS] Pipeline Finished Successfully!")
    print(f"Image Report: {image_file}")
    print("Push: ✓ Completed")
    print("="*50)

if __name__ == "__main__":
    main()
