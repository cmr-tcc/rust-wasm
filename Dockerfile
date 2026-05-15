# Base image
FROM node:22

# Avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

USER root

# Install dependencies
RUN apt update && apt install -y \
    curl \
    ca-certificates \
    build-essential \
    pkg-config \
    libssl-dev \
    git \
    wget \
    gnupg \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libc6 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libexpat1 \
    libfontconfig1 \
    libgbm1 \
    libgcc-s1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libstdc++6 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxshmfence1 \
    libxss1 \
    libxtst6 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Install Rust
ENV RUSTUP_HOME=/usr/local/rustup
ENV CARGO_HOME=/usr/local/cargo
ENV PATH=${CARGO_HOME}/bin:${PATH}
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y

# Add WebAssembly target
RUN rustup target add wasm32-unknown-unknown

# Install wasm-pack
RUN cargo install wasm-pack --version 0.13.1

# Verify installations
RUN node --version && \
    npm --version && \
    rustc --version && \
    cargo --version && \
    wasm-pack --version

# Default working directory
WORKDIR /app

COPY . .

RUN wasm-pack build --target web --out-dir web/pkg

RUN npm install

RUN chmod +x ./build.sh

CMD "./build.sh"