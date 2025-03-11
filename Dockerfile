FROM node:bookworm-slim

RUN apt update -y && apt upgrade -y

RUN apt install -y git ripgrep gh

RUN npm install -g @anthropic-ai/claude-code

WORKDIR /app
RUN git clone https://github.com/mak3r/vm-to-gpu

ENTRYPOINT [ "/bin/bash" ]

