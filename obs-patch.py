import os
import time
import argparse

_PACKAGE_MANAGERS = {1: 'apt', 2: 'pacman', 3: 'dnf', 4: 'zypper', 5: 'eopkg', 6: 'yum'}


def parse_cmd():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='script for NVFBC Patch into OBS, v1.1.')
    parser.add_argument('-s', '--silent', action='store_true', default=False,
                        help='set script to be silent and quick. Default False')
    parser.add_argument('-t', '--test', action='store_true', default=False,
                        help='Set to true to test script without executing install commands.')
    return parser.parse_args()


def print_splash(wait_time=1.5):
    print(" __   __   __              __  __   __    __       ___  __")
    print("/  \ |__) (_    |\ | \  / |_  |__) /     |__)  /\   |  /   |__|")
    print("\__/ |__) __)   | \|  \/  |   |__) \__   |    /--\  |  \__ |  |")
    print(" ")
    print("OBS NVFBC PATCH v1.1")
    print("github.com/liniuta/obs-nvfbc-patch")
    print("Getting required variables and loading the program..")
    print("Make sure you have OBS installed on your system and a network connection!")
    print(" ")
    time.sleep(wait_time)


def obs_patch(verbose=True, test=False):
    username = os.getlogin()
    working_directory = os.getcwd()
    if verbose and not test:
        print("Starting...")
        print("#" * 30)
        print("Patching Nvidia driver...")
        print("#" * 30)
        time.sleep(2)
    if not test:
        os.system("git clone https://github.com/keylase/nvidia-patch")
        os.chdir("nvidia-patch/")
        os.system("sudo ./patch-fbc.sh")
        os.chdir("..")

    if verbose and not test:
        print("#" * 30)
        print("Building OBS module..")
        print("#" * 30)
    if not test:
        os.system("git clone https://gitlab.com/fzwoch/obs-nvfbc")
        os.chdir("obs-nvfbc/")
        os.system("meson build")
        os.system("ninja -C build")

    if verbose and not test:
        time.sleep(2)
        print("#" * 30)
        print("Adding to OBS..")
        print("#" * 30)
    if not test:
        os.chdir(f"/home/{username}/.config/obs-studio/")
        os.mkdir("plugins")
        os.chdir(f"/home/{username}/.config/obs-studio/plugins/")
        os.mkdir("nvfbc")
        os.chdir(f"/home/{username}/.config/obs-studio/plugins/nvfbc/")
        os.mkdir("bin")
        os.chdir(f"/home/{username}/.config/obs-studio/plugins/nvfbc/bin/")
        os.mkdir("64bit")
        os.chdir(working_directory)
        os.chdir("obs-nvfbc/build/")
        os.system(f"cp nvfbc.so /home/{username}/.config/obs-studio/plugins/nvfbc/bin/64bit/")

    if verbose and not test:
        time.sleep(2)
        print(" ")
        print("Finished!")
        print("Now you can open OBS and add the new NVFBC source.")
        print("Enjoy!")
        print("#" * 30)
        print(" ")
        time.sleep(1)


def check_input(inp):
    common_misspellings = ['[', ']', ',', '\\', '|', ' ', '\"', '.']
    for occurrence in common_misspellings:
        inp = inp.replace(occurrence, '')
    if inp.isnumeric():
        return True, inp[0]
    only_numbers = [int(s) for s in inp.split() if s.isdigit()]
    if len(only_numbers) >= 1:
        return True, only_numbers[0]
    return False, None


def query_distro():
    print("What distro are you running?:")
    print(" [1] Debian based (Ubuntu, Linux Mint, Pop!_OS, elementary OS, MX Linux, Zorin OS etc.)")
    print(" [2] Arch based (Manjaro, EndeavourOS, Garuda Linux, Artix, Arco etc.) ")
    print(" [3] Fedora")
    print(" [4] openSUSE")
    print(" [5] Solus")
    print(" [6] Ones that use Yum")
    valid_input = False
    while not valid_input:
        input_str = input("Enter the number of your distro: ")
        valid_input, distro_id = check_input(input_str)
        if not valid_input: print("Number not recognized, please only enter a valid number.")
    return _PACKAGE_MANAGERS[int(distro_id)]


def get_manager():
    """Hacky way of getting the package manager without asking the user"""
    _package_managers = _PACKAGE_MANAGERS.values()
    for manager in _package_managers:
        if os.popen(manager).read() != '':
            return manager
    else:
        queried_manager = query_distro()
        return queried_manager


def get_manager_args(manager):
    if manager not in _PACKAGE_MANAGERS.values():
        raise ValueError('Package Manager not found in _PACKAGE_MANAGERS. Distro was not identified correctly.')
    if manager != 'pacman':
        return 'install'
    else:
        return '-S'


def main(test=False):
    args = parse_cmd()
    silent = args.silent
    if not silent: print_splash()

    if not test:
        username = os.getlogin()
        working_directory = os.getcwd()

    if not silent: time.sleep(1.5)
    manager = get_manager()
    manager_args = get_manager_args(manager)

    if not test:
        os.system(f"sudo {manager} {manager_args} libgl-dev meson ninja-build")
        obs_patch()
    else:
        print(f"sudo {manager} {manager_args} libgl-dev meson ninja-build")


if __name__ == '__main__':
    main(test=False)
