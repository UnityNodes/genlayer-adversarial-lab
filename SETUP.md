# Setup

The lab targets **Python 3.12+** and uses **Docker** for GenLayer Studio (localnet). Linux is recommended — GenLayer full nodes officially require 64-bit Linux, and Studio runs on Docker.

## 1. System dependencies (Ubuntu example)

```bash
sudo apt update
sudo apt install -y software-properties-common curl git
# Python 3.12
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3.12-dev
# Node.js LTS (for the GenLayer CLI)
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt install -y nodejs
# Docker (for GenLayer Studio / localnet)
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER   # re-login afterwards
```

Verify:
```bash
python3.12 --version   # >= 3.12
node --version
docker --version
```

## 2. GenLayer CLI

```bash
sudo npm install -g genlayer
genlayer --version
```

## 3. Python environment

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Verify:
```bash
genvm-lint --help
gltest --help
```

## 4. Reference patterns

The contracts reuse the canonical runtime `Depends` header from the official boilerplate. Clone it for reference:
```bash
git clone --depth 1 https://github.com/genlayerlabs/genlayer-project-boilerplate reference
head -1 reference/contracts/football_bets.py   # copy this Depends line into contracts
```

## 5. Studio (localnet) for integration tests

```bash
genlayer init          # starts Studio via Docker; UI ~ http://localhost:8080/, RPC http://127.0.0.1:4000/api
```

## 6. Run

```bash
genvm-lint check contracts/vulnerable/*.py contracts/hardened/*.py
pytest tests/direct/ -v                 # Docker NOT required
gltest tests/integration/ -v -s         # Studio required (step 5)
```
