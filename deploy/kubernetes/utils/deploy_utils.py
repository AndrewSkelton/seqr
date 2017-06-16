import glob
import logging
import os
import shutil
import time

from utils.constants import BASE_DIR, DEPLOYMENT_SCRIPTS
from utils.other_utils import retrieve_settings, check_kubernetes_context
from utils.seqrctl_utils import render, script_processor, template_processor, _run_shell_command

logger = logging.getLogger()


def deploy(deployment_label, component=None, output_dir=None, other_settings={}):
    """
    Args:
        deployment_label (string): one of the DEPLOYMENT_LABELS  (eg. "local", or "gcloud")
        component (string): optionally specifies one of the components from the DEPLOYABLE_COMPONENTS lists (eg. "postgres" or "phenotips").
            If this is set to None, all DEPLOYABLE_COMPONENTS will be deployed in sequence.
        output_dir (string): path of directory where to put deployment logs and rendered config files
        other_settings (dict): a dictionary of other key-value pairs for use during deployment
    """

    check_kubernetes_context(deployment_label)

    timestamp = time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime())
    output_dir = output_dir or "deployments/%(timestamp)s_%(deployment_label)s" % locals()

    # configure logging output
    log_dir = os.path.join(output_dir, "logs")
    if not os.path.isdir(log_dir):
        os.makedirs(log_dir)
    log_file_path = os.path.join(log_dir, "deploy.log")
    sh = logging.StreamHandler(open(log_file_path, "w"))
    sh.setLevel(logging.INFO)
    logger.addHandler(sh)
    logger.info("Starting log file: %(log_file_path)s" % locals())

    # parse config files
    settings = retrieve_settings(deployment_label)
    settings.update(other_settings)

    for key, value in settings.items():
        key = key.upper()
        settings[key] = value
        logger.info("%s = %s" % (key, value))

    # copy configs, templates and scripts to output directory
    output_base_dir = os.path.join(output_dir, 'configs')
    for file_path in glob.glob("templates/*/*.*") + glob.glob("templates/*/*/*.*"):
        file_path = file_path.replace('templates/', '')
        input_base_dir = os.path.join(BASE_DIR, 'templates')
        render(template_processor, input_base_dir, file_path, settings, output_base_dir)

    for file_path in glob.glob(os.path.join("scripts/*.sh")):
        render(script_processor, BASE_DIR, file_path, settings, output_dir)

    for file_path in glob.glob(os.path.join("scripts/*.py")):
        shutil.copy(file_path, output_base_dir)

    for file_path in glob.glob(os.path.join("config/*.yaml")):
        shutil.copy(file_path, output_base_dir)

    # copy docker directory to output directory
    docker_src_dir = os.path.join(BASE_DIR, "../docker/")
    docker_dest_dir = os.path.join(output_dir, "docker")
    logger.info("Copying %(docker_src_dir)s to %(docker_dest_dir)s" % locals())
    shutil.copytree(docker_src_dir, docker_dest_dir)

    # copy secrets directory
    secrets_src_dir = os.path.join(BASE_DIR, "secrets/%(deployment_label)s" % locals())
    secrets_dest_dir = os.path.join(output_dir, "secrets/%(deployment_label)s" % locals())
    logger.info("Copying %(secrets_src_dir)s to %(secrets_dest_dir)s" % locals())
    shutil.copytree(secrets_src_dir, secrets_dest_dir)

    # deploy
    if component:
        deployment_scripts = [s for s in DEPLOYMENT_SCRIPTS if 'init' in s or component in s or component.replace('-', '_') in s]
    else:
        deployment_scripts = DEPLOYMENT_SCRIPTS

    os.chdir(output_dir)
    logger.info("Switched to %(output_dir)s" % locals())

    for path in deployment_scripts:
        logger.info("=========================")
        _run_shell_command(path, verbose=True).wait()
