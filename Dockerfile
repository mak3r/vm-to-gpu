FROM node:bookworm-slim

RUN apt update -y && apt upgrade -y

RUN apt install -y git ripgrep gh build-essential vim rpm

RUN npm install -g @anthropic-ai/claude-code

WORKDIR /app
RUN git clone https://github.com/mak3r/vm-to-gpu 

WORKDIR /app/vm-to-gpu
RUN git checkout -b claude-code

ENTRYPOINT [ "/bin/bash" ]

