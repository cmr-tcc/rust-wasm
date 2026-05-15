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
COPY javascript/package.json javascript/package-lock.json ./javascript/

# Install Node dependencies
WORKDIR /app/javascript
RUN npm install
WORKDIR /app

# Copy the Rust files
COPY rust/ ./rust/

# Build the Rust
WORKDIR /app/rust
RUN wasm-pack build --target web --out-dir /app/javascript/web
WORKDIR /app

# Copy the rest of the project files
COPY . .

# Run benchmark
CMD ["./run.sh"]