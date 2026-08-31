#![no_std]
#![no_main]

mod framebuffer;

use bootloader_api::{entry_point, BootInfo};
use core::panic::PanicInfo;

use framebuffer::FrameBufferWriter;

entry_point!(kernel_main);

fn kernel_main(boot_info: &'static mut BootInfo) -> ! {
    // If the kernel reaches this point and framebuffer access works,
    // the entire screen should become bright red.
    if let Some(framebuffer) = boot_info.framebuffer.as_mut() {
        let mut writer = FrameBufferWriter::new(framebuffer);

        writer.clear(255, 0, 0);
    }

    loop {
        core::hint::spin_loop();
    }
}

#[panic_handler]
fn panic(_info: &PanicInfo) -> ! {
    loop {
        core::hint::spin_loop();
    }
}