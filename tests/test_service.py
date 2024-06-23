#!/usr/bin/env python
# coding: utf-8
from src.cinventory_pyrdo.computer.virtual import ServiceLocal


def test_service_local():

    vm = ServiceLocal()

    vm.name = "Tomcat"

    vm.add_dependency("java")

    vm.add_dependency("apache")

    vm.add_folders("/usr/local/tomcat")

    vm.add_folders("/usr/local/jvm")

    assert len(vm.dependency) > 0

    assert len(vm.folders) > 0
