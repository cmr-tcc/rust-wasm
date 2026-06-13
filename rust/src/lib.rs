pub mod fibonacci;
pub mod double;
pub mod nsieve;
pub mod fannkuch_redux;
pub mod n_body;
pub mod spectral_norm;
pub mod mandelbrot;
pub mod fasta;

#[cfg(not(target_arch = "wasm32"))]
pub mod bench;

#[cfg(target_arch = "wasm32")]
mod wasm_exports {
    use wasm_bindgen::prelude::*;

    #[wasm_bindgen]
    pub fn fibonacci(n: u64) -> u64 {
        crate::fibonacci::run(n)
    }

    #[wasm_bindgen]
    pub fn double(n: u64) -> u64 {
        crate::double::run(n)
    }

    #[wasm_bindgen]
    pub fn nsieve(n: u64) -> u64 {
        crate::nsieve::run(n)
    }

    #[wasm_bindgen]
    pub fn fannkuch_redux(n: u64) -> u64 {
        crate::fannkuch_redux::run(n)
    }

    #[wasm_bindgen]
    pub fn n_body(n: u64) -> u64 {
        crate::n_body::run(n)
    }

    #[wasm_bindgen]
    pub fn spectral_norm(n: u64) -> u64 {
        crate::spectral_norm::main(n)
    }

    #[wasm_bindgen]
    pub fn mandelbrot(n: u64) -> u64 {
        crate::mandelbrot::main(n)
    }

    #[wasm_bindgen]
    pub fn fasta(n: u64) -> u64 {
        crate::fasta::main(n)
    }
}
