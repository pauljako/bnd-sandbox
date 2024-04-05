#!/bin/python3
import sys
import os
import argparse
import time


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


QUOTE_SYMBOL_DOING = f" {Colors.BOLD}{Colors.OKCYAN}::{Colors.ENDC} "
QUOTE_SYMBOL_WARNING = f" {Colors.BOLD}{Colors.WARNING}::{Colors.ENDC} "
QUOTE_SYMBOL_INFO = f" {Colors.BOLD}{Colors.OKGREEN}::{Colors.ENDC} "
QUOTE_SYMBOL_ERROR = f" {Colors.BOLD}{Colors.FAIL}::{Colors.ENDC} "
QUOTE_SYMBOL_OUTPUT = f" {Colors.BOLD}{Colors.OKBLUE}::{Colors.ENDC} "


def install(container: str, pkg: str):
    path = os.path.realpath(os.path.join(os.getcwd(), pkg))
    os.system("if [ $(docker inspect -f '{{.State.Running}}' \"" + container + "\") = \"true\" ]; then echo Running; else docker start " + container + "; fi")
    time.sleep(0.2)
    if os.path.exists(path):
        print(f"{QUOTE_SYMBOL_DOING}Copying Local File{QUOTE_SYMBOL_DOING}")
        os.system("docker cp " + path + " " + container + ":/tmp/bnd-sandbox")
        print(f"{QUOTE_SYMBOL_DOING}Installing{QUOTE_SYMBOL_DOING}")
        os.system("sshpass -p boundaries ssh -X -p 2234 -o \"StrictHostKeyChecking=no\" -o \"UserKnownHostsFile=/dev/null\" boundaries@127.0.0.1 'sudo -i -u $USER boundaries install /tmp/bnd-sandbox'")
    else:
        os.system("sshpass -p boundaries ssh -X -p 2234 -o \"StrictHostKeyChecking=no\" -o \"UserKnownHostsFile=/dev/null\" boundaries@127.0.0.1 'sudo -i -u $USER bnd install " + pkg + "'")
        

def run(container: str, pkg_name: str, arguments: list):
    os.system("if [ $(docker inspect -f '{{.State.Running}}' \"" + container + "\") = \"true\" ]; then echo Running; else docker start " + container + "; fi")
    time.sleep(0.2)

    command = "sudo -i -u $USER boundaries run " + pkg_name
    for a in arguments:
        command = command + f" {a}"

    os.system("sshpass -p boundaries ssh -X -p 2234 -o \"StrictHostKeyChecking=no\" -o \"UserKnownHostsFile=/dev/null\" boundaries@127.0.0.1 '" + command + "'")


def shell(container: str):
    os.system("if [ $(docker inspect -f '{{.State.Running}}' \"" + container + "\") = \"true\" ]; then echo Running; else docker start " + container + "; fi")
    time.sleep(0.2)
    os.system("sshpass -p boundaries ssh -X -p 2234 -o \"StrictHostKeyChecking=no\" -o \"UserKnownHostsFile=/dev/null\" boundaries@127.0.0.1")


if __name__ == '__main__':
    parser = argparse.ArgumentParser("bnd-sandbox", description="Sandboxing for boundaries", allow_abbrev=False)

    command_parser = parser.add_subparsers(title="Actions", dest="action")

    shell_parser = command_parser.add_parser("shell", help="Connect to a Shell inside the Container")
    shell_parser.add_argument("container", help="The name of the Container")

    run_parser = command_parser.add_parser("run", help="Run a Package inside the Container")
    run_parser.add_argument("container", help="The name of the Container")
    run_parser.add_argument("package", help="Package Name")
    run_parser.add_argument("arguments", help="Arguments passed to the Application", nargs=argparse.REMAINDER)

    install_parser = command_parser.add_parser("install", help="Install A Package inside the Container")
    install_parser.add_argument("container", help="The name of the Container")
    install_parser.add_argument("package", help="The Path to the Package or the name of a Package to install with bnd-repo")

    args = parser.parse_args()

    if args.action == "shell":
        shell(args.container)
    elif args.action == "run":
        run(args.container, args.package, args.arguments)
    elif args.action == "install":
        install(args.container, args.package)
