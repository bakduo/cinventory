#!/usr/bin/env python
# coding: utf-8
from src.cinventory_pyrdo.computer.virtual import CommandExec

import pytest


def test_comand_exec():

    command = CommandExec()

    with pytest.raises(ValueError) as excinfo:
        command.exec("sudo ls -la /root")
    assert str(excinfo.value) == "Not permit sudo command"

    with pytest.raises(ValueError) as excinfo:
        command.exec("ls -la .;rm --help")
    assert str(excinfo.value) == "Not permit concat or pipeline or background command"

    with pytest.raises(ValueError) as excinfo:
        command.exec("ls -la && rm --help")
    assert str(excinfo.value) == "Not permit concat or pipeline or background command"

    with pytest.raises(ValueError) as excinfo:
        command.exec("ls -la &")
    assert str(excinfo.value) == "Not permit concat or pipeline or background command"

    command.exec("ls -la")

    assert len(command.output) > 0
