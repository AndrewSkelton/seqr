#!/usr/bin/env bash

SCRIPT_DIR="$( cd "$(dirname "$0")" ; pwd -P )"
source ${SCRIPT_DIR}/init_env.sh
set -x

if [ "$DELETE_BEFORE_DEPLOY" ]; then
    kubectl delete -f configs/cassandra/cassandra.${DEPLOY_TO_PREFIX}.yaml
fi

BUILD_ARG=
if [ "$BUILD" = true ]; then
    BUILD_ARG=--no-cache
fi

docker build $BUILD_ARG -t ${DOCKER_IMAGE_PREFIX}/cassandra docker/cassandra/
if [ "$DEPLOY_TO_PREFIX" = 'gcloud' ]; then
    docker tag ${DOCKER_IMAGE_PREFIX}/cassandra ${DOCKER_IMAGE_PREFIX}/cassandra:${TIMESTAMP}
    gcloud docker -- push ${DOCKER_IMAGE_PREFIX}/cassandra:${TIMESTAMP}
fi

# if the deployment doesn't exist yet, then create it, otherwise just update the image
kubectl apply -f configs/cassandra/cassandra.${DEPLOY_TO_PREFIX}.yaml --record
wait_until_pod_is_running cassandra
