import argparse
import boto3
import os


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["on", "off", "status"])
    parser.add_argument("host")
    parser.add_argument("--ssh_config_filepath", default="~/.ssh/config")
    args = parser.parse_args()
    return args


def find_aws_ec2_instance_details(host: str, ssh_config_filepath: str) -> dict:
    correct_host = None
    prefix = "ssh_switch_aws_"
    detail_keys = ["account_id", "region", "ec2_instance_id"]
    instance_details = {}
    with open(os.path.expanduser(ssh_config_filepath), "r") as openfile:
        for line in openfile:
            line = line.strip()
            if line.startswith("Host "):
                correct_host = line == "Host {}".format(host)
                continue
            if correct_host:
                for detail_key in detail_keys:
                    start_str = f"SetEnv {prefix}{detail_key}="
                    if line.startswith(start_str):
                        detail_value = line[len(start_str) :]
                        instance_details[detail_key] = detail_value
    for detail_key in detail_keys:
        if detail_key not in instance_details:
            raise AttributeError(
                f"Couldn't find {prefix}{detail_key} for {host} in {ssh_config_filepath}.\n"
                + f"Add `SetEnv {prefix}{detail_key}=<fill-in-blank>` property to the `{host}` block in {ssh_config_filepath}."
            )
    return instance_details


def get_caller_aws_account_id() -> str:
    sts_client = boto3.client("sts")
    try:
        caller_identity = sts_client.get_caller_identity()
    except sts_client.exceptions.ClientError as e:
        if "ExpiredToken" in str(e):
            raise EnvironmentError(
                "Can't use current AWS credentials due to an expired token. You should refresh them and then retry."
            )
        else:
            raise e
    account_id = caller_identity["Account"]
    return account_id


def status_action(host: str, instance) -> None:
    print("State of {}: {}".format(host, instance.state["Name"]))


def on_action(host: str, instance) -> None:
    if instance.state["Name"] == "running":
        print("State of {}: {}".format(host, instance.state["Name"]))
    else:
        instance.start()
        print("State of {}: {}".format(host, "starting"))
        instance.wait_until_running()
        print("State of {}: {}".format(host, instance.state["Name"]))


def off_action(host: str, instance) -> None:
    if instance.state["Name"] == "stopped":
        print("State of {}: {}".format(host, instance.state["Name"]))
    else:
        instance.stop()
        print("State of {}: {}".format(host, "stopping"))
        instance.wait_until_stopped()
        print("State of {}: {}".format(host, instance.state["Name"]))


def main() -> None:
    args = parse_args()
    instance_details = find_aws_ec2_instance_details(
        args.host, args.ssh_config_filepath
    )
    current_account = get_caller_aws_account_id()
    assert (
        instance_details["account_id"] == current_account
    ), f"Current credentials are from an different account {current_account}. Update credentials to account {instance_details['account_id']}."
    ec2 = boto3.resource("ec2", region_name=instance_details["region"])
    instance = ec2.Instance(instance_details["ec2_instance_id"])
    if args.action == "status":
        status_action(args.host, instance)
    elif args.action == "on":
        on_action(args.host, instance)
    elif args.action == "off":
        off_action(args.host, instance)
    else:
        ValueError('action must be `on`, `off` or `status`.')


if __name__ == "__main__":
    main()
