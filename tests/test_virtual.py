#!/usr/bin/env python
# coding: utf-8
from src.cinventory_pyrdo.computer.virtual import DebVirtual


def test_virtual_resources():

    vm = DebVirtual()

    assert len(vm.get_all_ip()) > 0

    assert vm.get_typeos().find("Ubuntu") > 0

    assert len(vm.get_list_pkg().items()) > 0
