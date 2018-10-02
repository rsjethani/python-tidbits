#!/usr/bin/env python3


import os
import pwd
import tempfile
import argparse
import subprocess as sub


# `LogLevel=error` allows for suppressing ssh banner
ssh_common_options = [
    "-o", "StrictHostKeyChecking=no",
    "-o", "LogLevel=error",
    "-o", "ControlMaster=auto",
    "-o", "ControlPath=.%r-%h-%p.sock",
    "-o", "ControlPersist=60",
    "-o", "PreferredAuthentications=publickey"
]


def remote_exec(auth, user, exec_line, host):
    exec_path, *exec_args =  exec_line.strip().split(" ", 1)
    exec_args = exec_args[0].strip() if exec_args else ""
    remote_path = remote_command(auth, user, "mktemp", host)

    # add auth, user and host
    auth_method, auth_path = auth.split(":")
    if auth_method == "key":
        auth_options = ["-i", auth_path, exec_path, "{}@{}:{}".format(user, host, remote_path)]
    elif auth_method == "config":
        auth_options = ["-F", auth_path, exec_path, "{}:{}".format(host, remote_path)]

    scp_cmd = "scp", *ssh_common_options, *auth_options
    try:
        errfile = tempfile.SpooledTemporaryFile(max_size=1000, mode='w+')
        sub.check_call(scp_cmd, stdout=sub.DEVNULL, stderr=errfile)
    except sub.CalledProcessError as e:
        errfile.seek(0, 0)
        return errfile.read().strip()

    command = ";".join(["chmod u+x {}".format(remote_path),
                "{} {}".format(remote_path, exec_args),
                "rm -f {}".format(remote_path)])
    return remote_command(auth, user, command, host)
    

def remote_command(auth, user, command, host):

    # add auth, user and host
    auth_method, auth_path = auth.split(":")
    if auth_method == "key":
        auth_options = ["-i", auth_path, "{}@{}".format(user, host)]
    elif auth_method == "config":
        auth_options = ["-F", auth_path, host]
    
    ssh_cmd = "ssh", "-T", *ssh_common_options, *auth_options, command
    try:
        errfile = tempfile.SpooledTemporaryFile(max_size=1000, mode='w+')
        return sub.check_output(ssh_cmd, stderr=errfile).decode().strip()
    except sub.CalledProcessError as e:
        errfile.seek(0, 0)
        return errfile.read().strip()


def main():
    ## parse commandline args ##
    parser = argparse.ArgumentParser()
    parser.add_argument("auth", help="path to file used for access......")
    parser.add_argument("command", help="sffdfsdfs")
    parser.add_argument("hosts", nargs="+", help="sdfsfs")
    parser.add_argument("-u", "--user", default=pwd.getpwuid(os.getuid())[0], help="sfsfdfS")
    args = parser.parse_args()

    method, command = args.command.split(":")
    if method == "cmd":
        remote_action = remote_command
    elif method == "exec":
        remote_action = remote_exec

    for host in args.hosts:
        print("----------------------------- {} ----------------------------".format(host))
        result = remote_action(args.auth, args.user, command, host)
        print(result)


if __name__ == "__main__":
    main()

