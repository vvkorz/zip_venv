#!/usr/bin python
# -*- coding: utf-8 -*-
"""
**This is WIP**

zips the virtual environment from which it is started into a specified folder

"""
import getpass
import os
import shutil
import subprocess


# Print iterations progress
def printProgressBar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end='\r')
    # Print New Line on Complete
    if iteration == total:
        print()


def zip_venv():
    """
    set the download folder that can be copied to the other machine

    :return:

    """

    print("Do you usually use proxy during you pip installations?")
    if input("Please enter y/n:") == "y":
        user = input("Please enter username:")
        user_pass = getpass.getpass(prompt='Please enter your password ')
        print("Would you like to specify the proxy?")
        print("e.g.: @proxy.host:8080")

        proxy = input("Please, enter desired proxy: ")

        proxy_string = "".join(["http://", user, ":", user_pass, proxy])
    else:
        proxy_string = False

    print()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    print("Default directory where files will be downloaded:")
    print(dir_path)
    if input("Would you like to change the above directory? y/n:") == "y":
        dir_path = input("directory: ")

    # getting venv
    try:
        from pip._internal.operations import freeze
    except ImportError:  # pip < 10.0
        from pip.operations import freeze

    # making directory to download files to
    if not os.path.exists(os.path.join(dir_path, "zipped_env", "pipfreeze")):
        os.makedirs(os.path.join(dir_path, "zipped_env", "pipfreeze"))

    env_packages = tuple(freeze.freeze())  # making tuple to be able to call len()
    requirements_file = []  # what to write to a new requirements.txt
    not_downloaded = []
    downloaded_packages = []
    FNULL = open(os.devnull, 'w')  # in order to redirect stout to nothing and have a nice progress bar =)
    for indx, package in enumerate(env_packages):

        if package[0:2] == "-e" or package[0:3] == "pip" or package[0:6] == "flake8" or package[0:11] == "pycodestyle" or package[0:8] == "pyflakes":
            # TODO download them too
            not_downloaded.append(package)

            # just a progress bar
            printProgressBar(indx, len(env_packages), prefix='Downloading packages:', suffix=" " * 30,
                             length=50)
        else:
            downloaded_packages.append(package.strip())
            # just a progress bar
            printProgressBar(indx, len(env_packages), prefix='Downloading packages:', suffix=package + " " * 30,
                             length=50)

            if package[0:2] != "-e" and package[0:3] != "pip":

                if proxy_string:
                    p = subprocess.Popen(["pip", "--proxy", proxy_string, "download", "-d",
                                          str(os.path.join(dir_path, "zipped_env", "pipfreeze")), "--no-deps", "--no-cache-dir",
                                          package], stdout=FNULL, stderr=subprocess.STDOUT, shell=True)
                else:
                    p = subprocess.Popen(["pip", "download", "-d",
                                          str(os.path.join(dir_path, "zipped_env", "pipfreeze")), "--no-deps",
                                          "--no-cache-dir",
                                          package], stdout=FNULL, stderr=subprocess.STDOUT, shell=True)
                p.communicate()  # waits till process finishes
                # to kill the process manually -> subprocess.Popen("TASKKILL /F /PID {pid} /T".format(pid=p.pid))
                requirements_file.append(package)

    printProgressBar(len(env_packages), len(env_packages), prefix='Downloading packages:', suffix="Done" + " " * 30,
                     length=50)

    if not_downloaded:
        print()
        print("The following packages where ignored...")
        for package in not_downloaded:
            print(package)

    # setuptools package must be installed first otherwise the process might break
    # thus let's create a separate installation for it that we will run before other installations
    setuptools_package = list(filter(lambda x: x if x[0:10] == "setuptools" else False, requirements_file))
    other = list(filter(lambda x: x if x[0:10] != "setuptools" else False, requirements_file))

    with open(os.path.join(dir_path, "zipped_env", "pipfreeze", "setuptools_package.txt"), "w") as f:
        f.write("--no-index --find-links=.\n")  # so that later we install only from this folder
        # put setuptools on top
        f.write("\n".join(setuptools_package))

    with open(os.path.join(dir_path, "zipped_env", "pipfreeze", "requirements.txt"), "w") as f:
        f.write("--no-index --find-links=.\n")  # so that later we install only from this folder
        f.write("\n".join(other))

    ###############################################################
    # Writing the .bat file to unzip the env on the server machine
    ###############################################################
    with open(os.path.join(dir_path, "zipped_env", "unzip_env.bat"), "w") as f:
        f.write("@ECHO OFF\n")
        f.write("ECHO==================================WARNING!=========================================\n")
        f.write("ECHO The following script will uninstall current packages from your virtual environment\n")
        f.write("ECHO \n")
        f.write("ECHO ==================================================================================\n")
        f.write("SET /P decision=Do you want to continue? (y / n):\n")
        f.write('IF "%decision%"=="n" GOTO Error\n')
        f.write("ECHO Brave decision! Let's go!\n")

    with open(os.path.join(dir_path, "zipped_env", "unzip_env.bat"), "a") as f:
        for package in downloaded_packages:
            f.write("pip uninstall -y " + package.split("==")[0] + "\n")

        # start installation of new requirements
        # first setuptools package
        f.write("cd pipfreeze\npip install -r setuptools_package.txt --ignore-installed\ncd ..\n")
        # then all other packages
        f.write("cd pipfreeze\npip install -r requirements.txt --ignore-installed\ncd ..\n")

    with open(os.path.join(dir_path, "zipped_env", "unzip_env.bat"), "a") as f:
        f.write("GOTO End\n:Error\nECHO Bye bye!!\n:End")

    print()
    # zip the entire folder so that it will be easier to copy it to a server
    shutil.make_archive(os.path.join(dir_path, "zipped_env"), 'zip', os.path.join(dir_path, "zipped_env"))

    print("Done! You can now copy zipped_env.zip to the other machine.")


if __name__ == "__main__":
    zip_venv()
