use std::path::PathBuf;

fn main() {
    let project_root = PathBuf::from(env!("CARGO_MANIFEST_DIR"));

    let kernel_path = project_root
        .join("../kernel/target/x86_64-unknown-none/debug/quantumos-kernel");

    if !kernel_path.exists() {
        panic!(
            "QuantumOS kernel not found at: {}",
            kernel_path.display()
        );
    }

    println!("cargo:rerun-if-changed=../kernel/src");
    println!("cargo:rerun-if-changed=../kernel/Cargo.toml");
    println!("cargo:rerun-if-changed=../kernel/target/x86_64-unknown-none/debug/quantumos-kernel");

    let bios_path = project_root.join("quantumos-bios.img");

    bootloader::BiosBoot::new(&kernel_path)
        .create_disk_image(&bios_path)
        .expect("Failed to create QuantumOS BIOS image");

    println!();
    println!("==========================================");
    println!("        QuantumOS BIOS IMAGE READY");
    println!("==========================================");
    println!("Image: {}", bios_path.display());
    println!("==========================================");
}