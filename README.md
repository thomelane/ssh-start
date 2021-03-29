# ssh-switch

Utility to switch Amazon EC2 instances on and off using SSH aliases.

## Install

### With [`pipx`](https://github.com/pipxproject/pipx)

[`pipx`](https://github.com/pipxproject/pipx) is a tool to install and run Python applications in isolated environments. With [`pipx`](https://github.com/pipxproject/pipx) you can install `ssh-switch` globally in it's own isolated environment, and it will always be available (no matter which environment you have activated at the time.)

1. `git clone` this package.
2. `pipx install .`

### With `pip`

1. `git clone` this package.
2. `pip install .`

## Setup

Since switch on/off commands reference SSH aliases (e.g. `dev.com`), you
must provide a mapping between SSH aliases and the instance in the
`~/.ssh/config` file. Custom properties are not allowed in these files so
instance details are provided as environment variables and set using
`SetEnv` properties. An instance is identified by it's AWS account ID,
region and EC2 instance ID. As example is shown below:

```bash
Host dev.com
    HostName 123.456.789
    User ec2-user
    IdentityFile ~/.ssh/keypair.pem
    SetEnv ssh_switch_aws_account_id=123456789123
    SetEnv ssh_switch_aws_region=us-west-2
    SetEnv ssh_switch_aws_ec2_instance_id=i-12345678912345678
```

## Usage

### Status

```bash
> ssh-switch status dev.com
State of dev.com: running
```

### On

```bash
> ssh-switch on dev.com
State of dev.com: starting
State of dev.com: running
```

### Off

```bash
> ssh-switch off dev.com
State of dev.com: stopping
State of dev.com: stopped
```
