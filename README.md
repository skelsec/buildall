# buildall

Script which installes/builds all of my projects.

# Prerequirements
This repo is using Porchetta Industries git server to fetch the projects, so you'd need to have a subscription as well as an SSH key for your account.

## For Python projects
You'd need to install rust
```
sudo apt install curl
curl https://sh.rustup.rs -sSf | sh -s -- -y
source "$HOME/.cargo/env"
```

## For Nim projects
You'd need to download and install the compiler from [here](https://nim-lang.org/install.html)

## For .NET projects
Yes.