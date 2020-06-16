# LinuxNano
# Used to control semiconductor equipment
... a work in progress

##Development Install
- `python3 -m venv venv` install a virtual environment
- `source venv/bin/activate`
- `pip install -r requirements.txt` install all the needed python packages
- `pip install -e .`  - install the linuxnano code as a package


##Notes
- `pydoc3 -p 9001` Launch python documentation on port 9001
- `sudo halcompile --install linuxnano/HAL/hardware_sim.comp` - compiles the hal file for testing / making fake pins
- `pytest 'tests/test_device_manual_view.py' -k 'test_two' -s` - Run tests starting with test_two
