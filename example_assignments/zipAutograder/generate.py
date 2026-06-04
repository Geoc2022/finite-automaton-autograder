import argparse
import shutil
import os
import stat

STUDENT_FILES_SOURCE = "student_files.txt"
NUMBER_OF_HOMEWORKS = 9
PYTHON_VERSION = "3.13"
STATIC_AUTOGRADER_FILES = [
    "setup.sh",
    "requirements.txt",
    "run_tests.py",
    "dfa.py",
    "grader.py",
]
RUN_AUTOGRADER_TEMPLATE = """#!/usr/bin/env bash

# This script was auto-generated /generate_autograder. Do not edit directly. 

STUDENT_FILES="{student_files}"

for file in $STUDENT_FILES; do
    if [ -f "/autograder/submission/$file" ]; then
        cp /autograder/submission/$file /autograder/source/$file
    else
        echo "Warning: File $file not found in submission."
    fi
done

cd /autograder/source
python{PYTHON_VERSION} run_tests.py
"""


def get_student_files(hw_num) -> list[str]:
    with open(f"hw{hw_num}/autograder/{STUDENT_FILES_SOURCE}", "r") as source_file:
        student_files = source_file.readline().strip().split(" ")
    return student_files


def run_autograder_exec(hw_num, student_files):
    # check if there's not already a custom run_autograder script
    if os.path.exists(f"hw{hw_num}/autograder/run_autograder"):
        print(f"Custom run_autograder script found for hw{hw_num}, skipping generation.")
        with open(f"hw{hw_num}/autograder/run_autograder", "r") as existing_script:
            run_autograder_script_str = existing_script.read()
        if PYTHON_VERSION not in run_autograder_script_str:
            print(f"Warning: Custom run_autograder script for hw{hw_num} does not use Python {PYTHON_VERSION}.")
        return
    run_autograder_script_str = RUN_AUTOGRADER_TEMPLATE.format(
        student_files=" ".join(student_files), PYTHON_VERSION=PYTHON_VERSION
    )

    script_path = f"hw{hw_num}/autograder/temp/run_autograder"
    with open(script_path, "w") as script_file:
        script_file.write(run_autograder_script_str)

        # Make the script executable
        existing_perms = os.stat(script_path).st_mode
        os.chmod(script_path, existing_perms | stat.S_IEXEC)


def zip_for_hw(hw_num):
    # homeworks with only written components can be skipped
    autograder_path = f"hw{hw_num}/autograder"
    if os.path.exists(autograder_path):
        try:
            # make a temporary directory to copy files to and clean up later
            temp_dir_path = f"{autograder_path}/temp"
            os.makedirs(temp_dir_path)

            # copy the generic hardcoded files
            for filename in STATIC_AUTOGRADER_FILES:
                shutil.copyfile(
                    f"zipAutograder/{filename}",
                    f"{autograder_path}/temp/{filename}",
                )

            # copy the hw specific autograder tests.
            shutil.copytree(
                f"{autograder_path}/tests",
                f"{autograder_path}/temp/tests",
            )

            student_files = get_student_files(hw_num)
            run_autograder_exec(hw_num, student_files)

            # copy over all the files that shouldn't be modified by students
            for item in os.listdir(f"hw{hw_num}/sol"):
                if item == "data":
                    shutil.copytree(
                        f"hw{hw_num}/sol/data",
                        f"{autograder_path}/temp/data",
                    )
                elif item not in student_files:
                    shutil.copyfile(
                        f"hw{hw_num}/sol/{item}",
                        f"{autograder_path}/temp/{item}",
                    )

            # copy over any other files in the autograder directory ignoring temp, tests, and student_files.txt
            for item in os.listdir(autograder_path):
                if item not in ["temp", "tests", STUDENT_FILES_SOURCE]:
                    item_path = os.path.join(autograder_path, item)
                    if os.path.isfile(item_path):
                        shutil.copyfile(
                            item_path,
                            os.path.join(f"{autograder_path}/temp", item),
                        )
                    elif os.path.isdir(item_path):
                        shutil.copytree(
                            item_path,
                            os.path.join(f"{autograder_path}/temp", item),
                        )

            # zip the autograder directory
            shutil.make_archive(
                f"{autograder_path}/autograder",
                "zip",
                root_dir=f"hw{hw_num}/autograder/temp",
            )

            print(f"Generated autograder zip for hw{hw_num} successfully.")

            # clean up the temporary directory
            shutil.rmtree(temp_dir_path)
        except Exception as e:
            print(f"Error generating autograder script for hw{hw_num}: {e}")


# expected to be run from the root directory of the repo
def main():
    parser = argparse.ArgumentParser(
        description="Generate autograder zip files for homework assignments."
    )

    parser.add_argument(
        "-hw",
        type=int,
        required=False,
        help="Which hw to generate the autograder zip for. Defaults to all hws.",
    )

    args = parser.parse_args()
    hw_numbers = [args.hw] if args.hw is not None else range(1, NUMBER_OF_HOMEWORKS + 1)

    for hw_num in hw_numbers:
        zip_for_hw(hw_num)


if __name__ == "__main__":
    main()
