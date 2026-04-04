import argparse

from backend.analyzer import analyze_resume, format_analysis


def main():
    parser = argparse.ArgumentParser(description="AI Resume Analyzer - Phase 1")
    parser.add_argument("file_path", help="Path to resume file (.pdf or .docx)")
    args = parser.parse_args()

    result = analyze_resume(args.file_path)
    print(format_analysis(result))


if __name__ == "__main__":
    main()
