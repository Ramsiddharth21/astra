import sys

from astra_core.pipeline.ai_full_pipeline import run_full_pipeline_with_ai
from astra_core.pipeline.scanall_pipeline import scan_all
from astra_core.pipeline.fixone_pipeline import fix_one_file


def main():
    if len(sys.argv) < 3:
        print("\nUsage:")
        print("  python main.py scanall <folder_path>")
        print("  python main.py fixone <file_path>")
        print("  python main.py fullscan_ai <folder_path>\n")
        sys.exit(1)

    command = sys.argv[1]
    path = sys.argv[2]

    if command == "scanall":
        report_file, report_data = scan_all(path)

        print("\nSCANALL completed.")
        print("Report saved as:", report_file)

        if report_data["files_with_errors"]:
            print("\nFiles with errors:\n")
            for idx, item in enumerate(report_data["files_with_errors"], start=1):
                print(f"{idx}. {item['file']}")
                for err in item["errors"]:
                    print("   -", err["type"])
        else:
            print("\nNo errors found in any file.\n")

    elif command == "fixone":
        result = fix_one_file(path)
        print("\nFIXONE completed.")
        print(result)

    elif command == "fullscan_ai":
        report_file = run_full_pipeline_with_ai(path)
        print("\nFULLSCAN_AI completed.")
        print("Report saved as:", report_file)

    else:
        print("\nInvalid command. Use: scanall, fixone, fullscan_ai\n")


if __name__ == "__main__":
    main()
