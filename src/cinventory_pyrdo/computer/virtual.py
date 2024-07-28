#!/usr/bin/env python
# coding: utf-8

import socket

from abc import ABC, abstractmethod

# from datetime import datetime

import logging

import platform

import distro

import configparser

import json

from shlex import quote

# from tempfile import NamedTemporaryFile

import subprocess


class CommandExec:

    def __init__(self):
        self.__cmd = None
        self.__stdout = None

    def __str__(self):
        return "Command class"

    @property
    def output(self):
        return self.__stdout

    def exec(self, value):
        # seconds = datetime.now().time().second
        tmp_value = value.strip()
        # sanitize check
        if tmp_value.find("sudo") >= 0:
            raise ValueError("Not permit sudo command")
        if (
            tmp_value.find(";") >= 0
            or (tmp_value.find("&&") >= 0)
            or (tmp_value.find("&") >= 0)
        ):
            raise ValueError("Not permit concat or pipeline or background command")

        sanitize = "{}".format(quote(tmp_value))

        self.__cmd = []

        # standard command alone parameter

        for cmd in sanitize.split(" "):
            self.__cmd.append(cmd.replace("'", ""))

        try:
            process_out = subprocess.Popen(
                self.__cmd,
                encoding="utf-8",
                shell=False,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            output, stderr = process_out.communicate(timeout=30)

            if stderr:
                raise ValueError("Error with the command: {}".format(self.__cmd))

            self.__stdout = str(output)

        except Exception as e:
            process_out.kill()
            output, error = process_out.communicate()
            logging.debug(
                "Exception on CommandExec method exec: {} {} {}".format(
                    e, output, error
                )
            )


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
            elif any("add__services" in B.__dict__ for B in C.__mro__):
                return True
            elif any("get__services" in B.__dict__ for B in C.__mro__):
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
        self.__uuid = DebVirtual.getUUID()
        self.__name = None
        self.__os = platform.system()
        self.__arch = platform.machine()
        self.__hostname = socket.gethostname()
        # self.__date = datetime.now()
        self.__kernel = platform.release()
        self.__services = []
        self.__productname = None

    def __str__(self):
        out_str = "Ubuntu vm hostname:"
        out_str += "{} os: {} arch: {}".format(self.__hostname, self.__os, self.__arch)
        return out_str

    @classmethod
    def valid_distro(cls, name):
        if name in ("debian", "mint", "ubuntu"):
            return True
        return False

    def product_name(self):
        try:
            if self.__productname is None:
                cmd = CommandExec()
                cmd.exec("cat /sys/class/dmi/id/product_name")
                name = cmd.output
                name = name.strip()
                cmd.exec("cat /sys/class/dmi/id/chassis_vendor")
                name += "-" + cmd.output
                name = name.strip()
                cmd.exec("cat /sys/class/dmi/id/bios_release")
                name += "-" + cmd.output
                name = name.strip()
                cmd.exec("cat /sys/class/dmi/id/sys_vendor")
                name += "-" + cmd.output
                name = name.strip()
                self.__productname = name.strip()
                return self.__productname
        except Exception as e:
            logging.DEBUG("Fail product_name {}".format(e))
            raise ValueError("Not permit product_name incomplete")

    @property
    def hostname(self):
        return self.__hostname

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = value

    def get_typeos(self):
        complete_os = platform.version()
        complete_os += " " + str(self.__os)
        complete_os += " Kernel: " + str(self.__kernel)
        complete_os += " version: " + str(distro.version())
        complete_os += " name: " + str(distro.name())
        return complete_os

    def get_all_ip(self):
        try:
            addresses = socket.getaddrinfo(self.__hostname, None)
            address_info = []
            for address in addresses:
                address_info.append(address[4][0])
            return address_info
        except Exception as e:
            logging.DEBUG("Fail get_all_ip {}".format(e))
            return []

    def _to_json_packages(self, stdout):

        json_stdout = {"packages": {}}

        for line in stdout.split("\n"):
            clean_line = line.strip()
            try:
                parts = clean_line.split("/")
                json_stdout["packages"][parts[0]] = parts[1]
            except Exception as e:
                logging.debug(
                    "Exception on DebVirtual json: {} with value: {}".format(e, parts)
                )

        return json_stdout

    def get_list_pkg(self):
        cmd = CommandExec()
        cmd.exec("apt list --installed")
        return self._to_json_packages(cmd.output)

    def get_services(self):
        return self.__services

    def add_services(self, value):
        self.__services.append(value)

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
            "id": self.__uuid,
        }

        return json.dumps(payload).encode("utf-8")


class ServiceLocal:

    def __init__(self):
        self.__name = None
        self.__dependency = []
        self.__folders = []

    @property
    def name(self):
        return self.__name

    @property
    def dependency(self):
        return self.__dependency

    @property
    def folders(self):
        return self.__folders

    @name.setter
    def name(self, value):
        self.__name = value

    def add_dependency(self, value):
        self.__dependency.append(value)

    def add_folders(self, value):
        self.__folders.append(value)
