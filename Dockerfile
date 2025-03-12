FROM node:bookworm-slim

RUN apt update -y && apt upgrade -y

RUN apt install -y git ripgrep gh build-essential vim rpm libgtk-3-0 libnotify-dev python3

RUN npm install -g @anthropic-ai/claude-code

WORKDIR /app
RUN git clone --single-branch --branch claude-code https://github.com/mak3r/vm-to-gpu 

WORKDIR /app/vm-to-gpu

ENTRYPOINT [ "/bin/bash" ]

