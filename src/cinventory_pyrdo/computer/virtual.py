#!/usr/bin/env python
# coding: utf-8

import socket

from abc import ABC, abstractmethod

from datetime import datetime

import logging

import platform

import distro

import os

import configparser

import json


class CommandExec:

    def __init__(self):
        self._cmd = None
        self._stdout = None
        self._admin = None

    def __str__(self):
        return "Command class"

    @property
    def file_name_out(self):
        return self._stdout

    def exec_simple_read(self, value):

        tmp_value = value.strip()
        if tmp_value.find("sudo") > 0:
            raise "Not permit sudo command"

        self._cmd = tmp_value

        try:
            return os.popen(self._cmd).read()
        except Exception as e:
            logging.debug("Exception on CommandExec method exec: {}".format(e))

    def exec(self, value):
        # seconds = datetime.now().time().second
        tmp_value = value.strip()
        if tmp_value.find("sudo") > 0:
            raise "Not permit sudo command"
        day = datetime.now().day
        self._stdout = "stdoutcmd{}.log".format(day)
        self._cmd = tmp_value + " > /tmp/" + self._stdout
        try:
            os.system(self._cmd)
        except Exception as e:
            logging.debug("Exception on CommandExec method exec: {}".format(e))


class VMUtil(ABC):

    @abstractmethod
    def get_all_ip(cls):
        pass

    @abstractmethod
    def get_typeos(cls):
        pass

    @abstractmethod
    def get_list_pkg(cls):
        pass

    @abstractmethod
    def add_services(cls):
        pass

    @abstractmethod
    def get_services(cls):
        pass

    @classmethod
    def __subclasshook__(cls, C):
        if cls is VMUtil:
            if any("get_all_ip" in B.__dict__ for B in C.__mro__):
                return True
            elif any("get_typeos" in B.__dict__ for B in C.__mro__):
                return True
            elif any("get_list_pkg" in B.__dict__ for B in C.__mro__):
                return True
            elif any("add_services" in B.__dict__ for B in C.__mro__):
                return True
            elif any("get_services" in B.__dict__ for B in C.__mro__):
                return True
        return NotImplemented


class DebVirtual(VMUtil):

    @classmethod
    def getUUID(cls):
        config = configparser.ConfigParser()
        config.read("/etc/cinventory/resource")
        ID = None
        if "id" in config["DEFAULT"]:
            ID = config["DEFAULT"]["id"]
        return ID

    def __init__(self):
        super().__init__()
        self._uuid = DebVirtual.getUUID()
        self._name = None
        self._os = platform.system()
        self._arch = platform.machine()
        self._hostname = socket.gethostname()
        self._date = datetime.now()
        self._kernel = platform.release()
        self._services = []
        self._productname = None

    def __str__(self):
        out_str = "Ubuntu vm hostname:"
        out_str += "{} os: {} arch: {}".format(self._hostname, self._os, self._arch)
        return out_str

    def product_name(self):
        cmd = CommandExec()
        name = cmd.exec_simple_read("cat /sys/class/dmi/id/product_name")
        name = name.strip()
        name += "-" + cmd.exec_simple_read("cat /sys/class/dmi/id/board_name")
        name = name.strip()
        name += "-" + cmd.exec_simple_read("cat /sys/class/dmi/id/product_sku")
        return name.strip()

    @property
    def hostname(self):
        return self._hostname

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    def get_typeos(self):
        complete_os = platform.version()
        complete_os += " " + str(self._os)
        complete_os += " Kernel: " + str(self._kernel)
        complete_os += " version: " + str(distro.version())
        complete_os += " name: " + str(distro.name())
        return complete_os

    def get_all_ip(self):
        try:
            addresses = socket.getaddrinfo(self._hostname, None)
            address_info = []
            for address in addresses:
                address_info.append(address[4][0])
            return address_info
        except Exception as e:
            logging.DEBUG("Fail get_all_ip {}".format(e))
            return []

    def _to_json_packages(self, stdout):

        json_stdout = {"packages": {}}

        with open("/tmp/" + stdout) as fpin:
            for nr, line in enumerate(fpin):
                clean_line = line.strip()
                try:
                    parts = clean_line.split("/")
                    json_stdout["packages"][parts[0]] = parts[1]
                except Exception as e:
                    logging.debug(
                        "Exception on DebVirtual json: {} with value: {}".format(
                            e, parts
                        )
                    )

        return json_stdout

    def get_list_pkg(self):
        cmd = CommandExec()
        cmd.exec("apt list --installed 2>/dev/null")
        return self._to_json_packages(cmd.file_name_out)

    def get_services(self):
        return self._services

    def add_services(self, value):
        self._services.append(value)

    def generate_report(self, configparser):

        sections = configparser.sections()

        for app in sections:
            serv_vm = ServiceLocal()
            serv_vm.name = app
            self.add_services(serv_vm)
            try:
                if "dependency" in configparser[app]:
                    for item in configparser[app]["dependency"].strip().split(","):
                        serv_vm.add_dependency(item)
                if "folders" in configparser[app]:
                    for item in configparser[app]["folders"].strip().split(","):
                        serv_vm.add_folders(item)
            except Exception as e:
                logging.debug("Exception {}".format(e))

        pkg = self.get_list_pkg()

        os = self.get_typeos()

        network = self.get_all_ip()

        service = self.get_services()

        service_tmp = {}

        for item in service:

            tmp_dependency = {}
            if item.dependency:
                tmp_dependency = item.dependency

            tmp_folders = {}
            if item.folders:
                tmp_folders = item.folders

            service_tmp[item.name] = {
                "dependency": tmp_dependency,
                "folders": tmp_folders,
            }

        payload = {"report": {}}

        payload["report"] = {
            "installed": pkg,
            "network": network,
            "os": os,
            "service": service_tmp,
            "resource_name": self.product_name(),
            "id": self._uuid,
        }

        return json.dumps(payload).encode("utf-8")


class ServiceLocal:

    def __init__(self):
        self._name = None
        self._dependency = []
        self._folders = []

    @property
    def name(self):
        return self._name

    @property
    def dependency(self):
        return self._dependency

    @property
    def folders(self):
        return self._folders

    @name.setter
    def name(self, value):
        self._name = value

    def add_dependency(self, value):
        self._dependency.append(value)

    def add_folders(self, value):
        self._folders.append(value)
