#!/bin/python3
"""
Buildozer action
================

It sets some environment variables, installs Buildozer, runs Buildozer and finds
output file.

You can read this file top down because functions are ordered by their execution
order.
"""

import os
import subprocess

# import sys
from os import environ as env
from pathlib import Path


def main():
    fix_home()
    install_buildozer(env["INPUT_BUILDOZER_VERSION"])
    change_directory(env["INPUT_REPOSITORY_ROOT"], env["INPUT_WORKDIR"])
    symlink_global_buildozer_dir()
    run_command(env["INPUT_COMMAND"])
    set_output(env["INPUT_REPOSITORY_ROOT"], env["INPUT_WORKDIR"])
    show_env()
    show_buildozer_global_dir()


def fix_home():
    # GitHub sets HOME to /github/home, but Buildozer is installed to /home/user. Change HOME to user's home
    env["HOME"] = env["HOME_DIR"]


def install_buildozer(buildozer_version):
    # Install required Buildozer version
    print("::group::Installing Buildozer")
    pip_install = "python -m pip install --upgrade".split()
    if buildozer_version == "stable":
        # Install stable buildozer from PyPI
        subprocess.check_call([*pip_install, "buildozer"])
    elif os.path.exists(buildozer_version) and os.path.exists(
        os.path.join(buildozer_version, "buildozer", "__init__.py")
    ):
        # Install from local directory
        subprocess.check_call([*pip_install, buildozer_version])
    elif buildozer_version.startswith("git+"):
        # Install from specified git+ link
        subprocess.check_call([*pip_install, buildozer_version])
    elif buildozer_version == "":
        # Just do nothing
        print(
            "::warning::Buildozer is not installed because "
            "specified buildozer_version is nothing."
        )
    else:
        # Install specified ref from repository
        subprocess.check_call(
            [
                *pip_install,
                f"git+https://github.com/kivy/buildozer.git@{buildozer_version}",
            ]
        )
    print("::endgroup::")


def change_directory(repository_root, workdir):
    directory = os.path.join(repository_root, workdir)
    # Change directory to workir
    if not os.path.exists(directory):
        print("::error::Specified workdir is not exists.")
        exit(1)
    os.chdir(directory)


def symlink_global_buildozer_dir():
    env["BUILDOZER_DEFAULT"] = f"{env['HOME']}/.buildozer"
    env["BUILDOZER_GLOBAL"] = (
        f"{env['GITHUB_WORKSPACE']}/{env['INPUT_REPOSITORY_ROOT']}/.buildozer_global"
    )
    global_buildozer_dir = Path(env["BUILDOZER_GLOBAL_DIR"])
    default_buildozer_dir = Path(env["BUILDOZER_DEFAULT_DIR"])
    print(
        f"::group::Creating symlink from {global_buildozer_dir} to {default_buildozer_dir}."
    )
    global_buildozer_dir.mkdir()
    default_buildozer_dir.symlink_to(global_buildozer_dir, target_is_directory=True)
    print("::endgroup::")


def run_command(command):
    # Run command
    retcode = subprocess.check_call(command, shell=True)
    if retcode:
        print(f'::error::Error while executing command "{command}"')
        exit(1)


def set_output(repository_root, workdir):
    if not os.path.exists("bin"):
        print("::error::Output directory does not exist. See Buildozer log for error")
        exit(1)
    filename = [
        file for file in os.listdir("bin") if os.path.isfile(os.path.join("bin", file))
    ][0]
    path = os.path.normpath(os.path.join(repository_root, workdir, "bin", filename))
    # Run with sudo to have access to GITHUB_OUTPUT file
    subprocess.check_call(
        [
            "sudo",
            "bash",
            "-c",
            f"echo 'filename={path}' >> {os.environ['GITHUB_OUTPUT']}",
        ]
    )


def show_env():
    print("::group::Showing env variables.")
    for k, v in sorted(env.items()):
        print(f"{k}={v}")
    print("::endgroup::")


def show_buildozer_global_dir():
    print("::group::Showing BUILDOZER_GLOBAL_DIR contents.")
    for f in Path(env["BUILDOZER_GLOBAL_DIR"]).iterdir():
        print(f)
    print("::endgroup::")


if __name__ == "__main__":
    main()
