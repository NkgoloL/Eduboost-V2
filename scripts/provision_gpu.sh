#!/usr/bin/env bash
set -euo pipefail

# Provision an AWS g5.xlarge Spot Instance for EduBoost LLM fine-tuning.
#
# Required:
#   AWS CLI v2 configured with credentials
#   KEY_NAME=<existing-ec2-key-pair> ./scripts/provision_gpu.sh
#
# Optional:
#   AWS_REGION=af-south-1|us-east-1|...    Default: current AWS CLI region or us-east-1
#   INSTANCE_TYPE=g5.xlarge                 Default: g5.xlarge
#   MAX_SPOT_PRICE=0.45                     Default: 0.45 USD/hour
#   MAX_RUNTIME_HOURS=180                   Default: 180, keeps compute inside an $80-ish cap
#   VOLUME_SIZE_GB=100                      Default: 100
#   SSH_CIDR=1.2.3.4/32                     Default: your detected public IP /32
#   HTTP_CIDR=1.2.3.4/32                    Default: same as SSH_CIDR
#   ALLOW_HTTP_PORT=8080                    Default: 8080
#   R2_BUCKET_NAME=eduboost-assets          Passed through as an instance tag only

AWS_REGION="${AWS_REGION:-$(aws configure get region 2>/dev/null || true)}"
AWS_REGION="${AWS_REGION:-us-east-1}"
INSTANCE_TYPE="${INSTANCE_TYPE:-g5.xlarge}"
MAX_SPOT_PRICE="${MAX_SPOT_PRICE:-0.45}"
MAX_RUNTIME_HOURS="${MAX_RUNTIME_HOURS:-180}"
VOLUME_SIZE_GB="${VOLUME_SIZE_GB:-100}"
ALLOW_HTTP_PORT="${ALLOW_HTTP_PORT:-8080}"
R2_BUCKET_NAME="${R2_BUCKET_NAME:-eduboost-assets}"
KEY_NAME="${KEY_NAME:-}"

if [[ -z "${KEY_NAME}" ]]; then
  echo "KEY_NAME is required. Create or choose an EC2 key pair, then run:"
  echo "  KEY_NAME=<your-key-pair> $0"
  exit 2
fi

for cmd in aws curl; do
  if ! command -v "${cmd}" >/dev/null 2>&1; then
    echo "Missing required command: ${cmd}"
    exit 2
  fi
done

echo "Using region: ${AWS_REGION}"

VPC_ID="$(aws ec2 describe-vpcs \
  --region "${AWS_REGION}" \
  --filters Name=isDefault,Values=true \
  --query 'Vpcs[0].VpcId' \
  --output text)"

if [[ -z "${VPC_ID}" || "${VPC_ID}" == "None" ]]; then
  echo "No default VPC found in ${AWS_REGION}. Set VPC/subnet support before provisioning."
  exit 1
fi

SUBNET_ID="$(aws ec2 describe-subnets \
  --region "${AWS_REGION}" \
  --filters "Name=vpc-id,Values=${VPC_ID}" Name=default-for-az,Values=true \
  --query 'Subnets[0].SubnetId' \
  --output text)"

if [[ -z "${SUBNET_ID}" || "${SUBNET_ID}" == "None" ]]; then
  echo "No default subnet found for ${VPC_ID}."
  exit 1
fi

MY_IP="$(curl -fsS https://checkip.amazonaws.com | tr -d '[:space:]')"
SSH_CIDR="${SSH_CIDR:-${MY_IP}/32}"
HTTP_CIDR="${HTTP_CIDR:-${SSH_CIDR}}"
SG_NAME="${SG_NAME:-eduboost-gpu-training}"

SG_ID="$(aws ec2 describe-security-groups \
  --region "${AWS_REGION}" \
  --filters "Name=group-name,Values=${SG_NAME}" "Name=vpc-id,Values=${VPC_ID}" \
  --query 'SecurityGroups[0].GroupId' \
  --output text 2>/dev/null || true)"

if [[ -z "${SG_ID}" || "${SG_ID}" == "None" ]]; then
  SG_ID="$(aws ec2 create-security-group \
    --region "${AWS_REGION}" \
    --group-name "${SG_NAME}" \
    --description "EduBoost GPU training access" \
    --vpc-id "${VPC_ID}" \
    --query 'GroupId' \
    --output text)"
fi

authorize_ingress() {
  local port="$1"
  local cidr="$2"
  aws ec2 authorize-security-group-ingress \
    --region "${AWS_REGION}" \
    --group-id "${SG_ID}" \
    --ip-permissions "IpProtocol=tcp,FromPort=${port},ToPort=${port},IpRanges=[{CidrIp=${cidr}}]" \
    >/dev/null 2>&1 || true
}

authorize_ingress 22 "${SSH_CIDR}"
authorize_ingress "${ALLOW_HTTP_PORT}" "${HTTP_CIDR}"

AMI_ID="$(aws ec2 describe-images \
  --region "${AWS_REGION}" \
  --owners amazon \
  --filters 'Name=name,Values=Deep Learning Base OSS Nvidia Driver GPU AMI (Ubuntu 22.04)*' \
  --query 'sort_by(Images, &CreationDate)[-1].ImageId' \
  --output text)"

if [[ -z "${AMI_ID}" || "${AMI_ID}" == "None" ]]; then
  echo "Could not locate the latest AWS Deep Learning Base OSS NVIDIA GPU Ubuntu 22.04 AMI."
  exit 1
fi

USER_DATA="$(mktemp)"
cat >"${USER_DATA}" <<EOF
#cloud-config
package_update: true
packages:
  - git
  - tmux
  - htop
  - nvtop
  - python3-pip
runcmd:
  - [ bash, -lc, "shutdown -h +$((MAX_RUNTIME_HOURS * 60)) 'EduBoost GPU budget guard: max runtime reached'" ]
  - [ bash, -lc, "mkdir -p /opt/eduboost && chown ubuntu:ubuntu /opt/eduboost" ]
  - [ bash, -lc, "echo 'R2 bucket: ${R2_BUCKET_NAME}' >/opt/eduboost/training-notes.txt" ]
EOF

echo "Requesting ${INSTANCE_TYPE} Spot Instance with AMI ${AMI_ID}"

INSTANCE_ID="$(aws ec2 run-instances \
  --region "${AWS_REGION}" \
  --image-id "${AMI_ID}" \
  --instance-type "${INSTANCE_TYPE}" \
  --key-name "${KEY_NAME}" \
  --subnet-id "${SUBNET_ID}" \
  --security-group-ids "${SG_ID}" \
  --instance-initiated-shutdown-behavior terminate \
  --instance-market-options "MarketType=spot,SpotOptions={MaxPrice=${MAX_SPOT_PRICE},SpotInstanceType=one-time,InstanceInterruptionBehavior=terminate}" \
  --block-device-mappings "DeviceName=/dev/sda1,Ebs={VolumeSize=${VOLUME_SIZE_GB},VolumeType=gp3,DeleteOnTermination=true}" \
  --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=eduboost-gpu-training},{Key=Project,Value=EduBoost},{Key=Purpose,Value=LLM-FineTuning},{Key=MaxRuntimeHours,Value=${MAX_RUNTIME_HOURS}},{Key=R2Bucket,Value=${R2_BUCKET_NAME}}]" \
  --user-data "file://${USER_DATA}" \
  --query 'Instances[0].InstanceId' \
  --output text)"

rm -f "${USER_DATA}"

echo "Instance requested: ${INSTANCE_ID}"
echo "Waiting for public IP..."
aws ec2 wait instance-running --region "${AWS_REGION}" --instance-ids "${INSTANCE_ID}"

PUBLIC_IP="$(aws ec2 describe-instances \
  --region "${AWS_REGION}" \
  --instance-ids "${INSTANCE_ID}" \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text)"

echo "Ready."
echo "  Instance ID: ${INSTANCE_ID}"
echo "  Public IP:   ${PUBLIC_IP}"
echo "  SSH:         ssh -i <path-to-key.pem> ubuntu@${PUBLIC_IP}"
echo "  HTTP port:   ${ALLOW_HTTP_PORT} open to ${HTTP_CIDR}"
echo "  Auto-stop:   terminate after ${MAX_RUNTIME_HOURS} hours unless changed"
