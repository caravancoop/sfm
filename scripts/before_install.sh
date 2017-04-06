#!/bin/bash

# Change all <VARS_IN_BRACKETS>

# Trigger failed deployment if the server encounters errors, i.e.
# issues with your supervisor or nginx configs or your deploy
# scripts.
set -euo pipefail

# Create a fresh project directory. (This is mainly to ensure that 
# these scripts work on a bare server.)
rm -Rf /home/datamade/sfm-cms
mkdir -p /home/datamade/sfm-cms

# Change into the directory where your changes were downloaded, 
# make the datamade user the owner of the files therein, and
# decrypt files encrypted in Blackbox.
cd /opt/codedeploy-agent/deployment-root/$DEPLOYMENT_GROUP_ID/$DEPLOYMENT_ID/deployment-archive/ && \
chown -R datamade.datamade . && \
sudo -H -u datamade blackbox_postdeploy
