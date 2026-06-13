pub mod fibonacci;
pub mod double;
pub mod nsieve;
pub mod fannkuch;
pub mod nbody;

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
    pub fn fannkuch(n: u64) -> u64 {
        crate::fannkuch::run(n)
    }

    #[wasm_bindgen]
    pub fn nbody(n: u64) -> u64 {
        crate::nbody::run(n)
    }
}
