import configparser

from src.cinventory_pyrdo.computer.virtual import DebVirtual, ServiceLocal

import logging

# uncomment you have a remote server
# import requests

import json


def test_main_procesing():
    config = configparser.ConfigParser()
    config.read("tests/config")
    vm = DebVirtual()
    sections = config.sections()

    assert len(sections) == 3

    for app in sections:
        serv_vm = ServiceLocal()
        serv_vm.name = app
        vm.add_services(serv_vm)
        try:
            if "dependency" in config[app]:
                for item in config[app]["dependency"].strip().split(","):
                    serv_vm.add_dependency(item)
            if "folders" in config[app]:
                for item in config[app]["folders"].strip().split(","):
                    serv_vm.add_folders(item)
        except Exception as e:
            logging.debug("Exception {}".format(e))

    assert len(vm.get_services()) == 3

    for item in vm.get_services():
        assert len(item.name) > 0


def test_payload_json():
    config = configparser.ConfigParser()

    config.read("tests/config")

    vm = DebVirtual()

    report = vm.generate_report(config)

    valid = json.loads(report)

    assert valid["report"] is not None
    assert valid["report"]["os"] is not None
    assert valid["report"]["installed"] is not None
    assert valid["report"]["network"] is not None
    assert valid["report"]["service"] is not None
    assert len(valid["report"]["service"]) == 3

    # only enable for remote server test
    # response = requests.post(
    #     "http://localhost:5001/report",
    #     data=report,
    #     headers={"Content-Type": "application/json"},
    # )

    # assert response.status_code == 200
