from kubernetes import (
    client,
    watch as k8s_watch,
    config,
)
import logging
import click
import pyfiglet as pf
import datetime as datetime
from logger import setup_logger
from validate import validate_secret_label

CLIENT_SOCKET_TIMEOUT = None
SERVER_SOCKET_TIMEOUT = None

TRIGGERING_OPERATIONS = [
    "ADDED",
    "MODIFIED",
]

config.load_kube_config()

secrets_registry = []


@click.group()
@click.option("--verbosity", default="INFO", help="verbosity of the logger")
def cli(verbosity):
    setup_logger(
        verbosity,
        "REDEPLOYER",
    )


def redeploy(
    redeployments: dict,
):
    # inspired by
    # https://stackoverflow.com/questions/65996468/python-client-euqivelent-of-kubectl-rollout-restart-deployment
    v1 = v1 = client.AppsV1Api()
    now = datetime.datetime.now(datetime.UTC)
    now = str(now.isoformat("T") + "Z")
    logger = logging.getLogger("REDEPLOYER")
    body = {
        "spec": {
            "template": {
                "metadata": {
                    "annotations": {"kubectl.kubernetes.io/restartedAt": now}
                }
            }
        }
    }
    for deployment in redeployments.values():
        try:
            v1.patch_namespaced_deployment(
                deployment["name"],
                deployment["namespace"],
                body,
                pretty="true",
            )
        except client.rest.ApiException as e:
            logger.error("Did not succeed in redeploying! Details below:")
            logger.error(e)


@click.command()
def watch():
    v1 = client.CoreV1Api()
    logger = logging.getLogger("REDEPLOYER")
    logger.info("Starting to watch for secret changes...")
    w = k8s_watch.Watch()
    for event in w.stream(
        v1.list_secret_for_all_namespaces,
        _request_timeout=CLIENT_SOCKET_TIMEOUT,
        timeout_seconds=SERVER_SOCKET_TIMEOUT,
    ):
        obj_name = event["object"].metadata.name
        obj_type = event["type"]
        logger.debug(f"New event: '{obj_type}', for object: '{obj_name}'")
        labels = event["object"].metadata.labels
        valid = True
        if labels:
            redeployments = {}
            for label_name, label_value in labels.items():
                try:
                    updated_redeployments = validate_secret_label(
                        label_name,
                        label_value,
                        redeployments,
                    )
                    if updated_redeployments:
                        redeployments = updated_redeployments
                except ValueError as e:
                    logger.error(e)
                    valid = False
                    break
            for deployment in redeployments.values():
                if len(deployment.keys()) < 2:
                    logger.warning(
                        f"Redeployment label '{deployment}' not ready. "
                        "Must have at least 2 keys. Skipping..."
                    )
                    valid = False
            if valid and redeployments:
                if obj_type == "ADDED" and obj_name not in secrets_registry:
                    logger.debug(
                        "Not firing event on first secret creation. "
                        "Adding to the registry for now."
                    )
                    secrets_registry.append(obj_name)
                elif obj_type in TRIGGERING_OPERATIONS:
                    logger.info(
                        f"Secret '{obj_name}' has changed "
                        "and is redeployable. "
                        f"Triggering redeployment..."
                    )
                    redeploy(dict(redeployments))
                    logger.info(
                        f"Finished redeployment for secret '{obj_name}'."
                    )
                else:
                    logger.debug(
                        f"Secret '{obj_name}' has not changed. " "Skipping..."
                    )

    logger.info("Finished watching for secret changes...")


cli.add_command(watch)

if __name__ == "__main__":
    click.secho(
        pf.figlet_format("REDEPLOYER"),
        fg="blue",
        bg=None,
        bold=True,
    )
    cli()