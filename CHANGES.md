CInventory_pyrdo
===
- 1.0.6
  * Fix version distro >=1.6.0. Problem, No matching distribution found for distro on Ubuntu 22 LTS.
  * function product_name, remove board_name and product_sku. Add chassis_vendor, sys_vendor and bios_release.

- 1.0.5
  * Remove dependency without use, psutil.

- 1.0.4
  * Fix Starting a process with a shell, possible injection detected, security issue
  * Fix Requests call without timeout
  * Fix subprocess call - check for execution of untrusted input and Consider possible security implication associated with the subprocess module. https://github.com/PyCQA/bandit/issues/333
  * Fix Probable insecure usage of temp file/directory
  * Fix find string position 0 for exec command.
  * add command testing
  
- 1.0.3
  * Add parameter Type for support only distros based in apt.
  * Fix resource_name json for linux distro.
  * Update readme, makefile, classifiers

- 1.0.2
  * Change attribute protected to private.
  * Change product_name for exec only one at once

- 1.0.1

  * support proyect toml format
  * remove high version requests

- 1.0.0

  * Initial release.