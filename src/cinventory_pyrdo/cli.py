#!/usr/bin/env python
# coding: utf-8

import logging
import argparse
from cinventory_pyrdo import VERSION
from cinventory_pyrdo.computer.virtual import DebVirtual
import sys
import configparser
import json
import requests


def main():
    server_remote = None
    report_generate = False
    config = configparser.ConfigParser()
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "-v", "--version", help="show program version", action="store_true"
        )
        parser.add_argument("-t", "--type", help="type distro debian, mint and ubuntu")

        parser.add_argument("-s", "--server", help="set remote server to send report")
        parser.add_argument(
            "-g", "--generate", help="enable to generate report", action="store_true"
        )
        args = parser.parse_args()

        if args.version:
            print("CInventory: v{}".format(VERSION))
            sys.exit(0)
        if args.server:
            server_remote = args.server
        if args.type:
            server_distro = args.type
        if args.generate:
            report_generate = True

    except Exception as err:
        logging.debug("Exception on main cinventory cmdline: {}".format(err))

    if server_remote is not None and report_generate and server_distro:
        config.read("/etc/cinventory/resource")
        if DebVirtual.valid_distro(server_distro):
            vm = DebVirtual()
            report = vm.generate_report(config)
            requests.post(
                server_remote,
                data=report,
                headers={"Content-Type": "application/json"},
            )
        else:
            raise "Don't support distro {} : use --help".format(server_distro)

    elif server_remote is None and report_generate and server_distro:
        config.read("/etc/cinventory/resource")
        if DebVirtual.valid_distro(server_distro):
            vm = DebVirtual()
            return json.loads(vm.generate_report(config))
        else:
            raise "Don't support distro {} : use --help".format(server_distro)
    else:
        raise "You need parameter for works: use --help"

    return 0


if __name__ == "__main__":
    response = main()
    if response == 0:
        print(0)
    else:
        print(json.dumps(response, indent=4, sort_keys=True))
