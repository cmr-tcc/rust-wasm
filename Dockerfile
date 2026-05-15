# Base image
FROM ghcr.io/puppeteer/puppeteer:latest

# Avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt update && apt install -y curl && rm -rf /var/lib/apt/lists/*

# Install Node.js (LTS)
RUN curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - && \
    apt update && apt install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

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