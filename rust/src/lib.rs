pub mod fibonacci;
pub mod double;

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
}
