# zip python venv

A script for transfering a python virtual environment to a remote Windows machine with no access to internet. 

## About

The script downloads wheels of all packages in virtual env and zips everything, creating a script to unzip it all on remote machine. 

## Usage

1. Activate your virtual environment

2. run the following command
```
python zip_venv.py
```

3. follow instructions

4. copy resulted .zip to the remote machine

5. activate virtual environment on the remote machine

6. run the following command
```
unzip_env.bat
```

## Author

* **Vladimir Korzinov** - *Initial work* - [vvkorz](https://github.com/vvkorz)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE) file for details
