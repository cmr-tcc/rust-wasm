# Node 24 and Puppeteer image
FROM ghcr.io/puppeteer/puppeteer:24.43.1

# Required for Puppeteer
USER root

# Install Rust
ENV RUSTUP_HOME=/usr/local/rustup
ENV CARGO_HOME=/usr/local/cargo
ENV PATH=${CARGO_HOME}/bin:${PATH}
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y --default-toolchain 1.95.0

# Set Rust environment variables
RUN rustup target add wasm32-unknown-unknown

# Install wasm-pack
RUN cargo install wasm-pack --version 0.14.0

# Setup current directory
WORKDIR /app

# Copy Node package files
COPY package.json package-lock.json ./

# Install Node dependencies
RUN npm install

# Copy the rest of the project files
# 🌠 Do this in the end, copy first only Rust to improve cache, when i change JS it re-runs the layer below, so split between node and rust to compare later
COPY . .

# Build the Rust code to WebAssembly
RUN wasm-pack build --target web --out-dir web/pkg

# Run benchmark
CMD ["./build.sh"]