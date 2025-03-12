FROM node:bookworm-slim

RUN apt update -y && apt upgrade -y

RUN apt install -y git ripgrep gh build-essential vim rpm

RUN npm install -g @anthropic-ai/claude-code

WORKDIR /app
RUN git clone --single-branch --branch claude-code https://github.com/mak3r/vm-to-gpu 

WORKDIR /app/vm-to-gpu

COPY packaging/vm-to-gpu.spec /app/vm-to-gpu/packaging/vm-to-gpu.spec

ENTRYPOINT [ "/bin/bash" ]

