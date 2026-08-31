use bootloader_api::info::{FrameBuffer, PixelFormat};

pub struct FrameBufferWriter<'a> {
    framebuffer: &'a mut FrameBuffer,
}

impl<'a> FrameBufferWriter<'a> {
    pub fn new(framebuffer: &'a mut FrameBuffer) -> Self {
        Self { framebuffer }
    }

    pub fn clear(&mut self, red: u8, green: u8, blue: u8) {
        let info = self.framebuffer.info();

        self.fill_rect(
            0,
            0,
            info.width,
            info.height,
            red,
            green,
            blue,
        );
    }

    pub fn fill_rect(
        &mut self,
        x: usize,
        y: usize,
        width: usize,
        height: usize,
        red: u8,
        green: u8,
        blue: u8,
    ) {
        let info = self.framebuffer.info();

        if x >= info.width || y >= info.height {
            return;
        }

        let end_x = x
            .saturating_add(width)
            .min(info.width);

        let end_y = y
            .saturating_add(height)
            .min(info.height);

        let bytes_per_pixel = info.bytes_per_pixel;
        let stride = info.stride;
        let pixel_format = info.pixel_format;

        if bytes_per_pixel == 0 {
            return;
        }

        let buffer = self.framebuffer.buffer_mut();

        for py in y..end_y {
            for px in x..end_x {
                let pixel_index = py
                    .saturating_mul(stride)
                    .saturating_add(px);

                let offset = pixel_index
                    .saturating_mul(bytes_per_pixel);

                if offset >= buffer.len() {
                    continue;
                }

                match pixel_format {
                    PixelFormat::Bgr => {
                        Self::write_byte(
                            buffer,
                            offset,
                            blue,
                        );

                        if bytes_per_pixel >= 2 {
                            Self::write_byte(
                                buffer,
                                offset + 1,
                                green,
                            );
                        }

                        if bytes_per_pixel >= 3 {
                            Self::write_byte(
                                buffer,
                                offset + 2,
                                red,
                            );
                        }
                    }

                    PixelFormat::Rgb => {
                        Self::write_byte(
                            buffer,
                            offset,
                            red,
                        );

                        if bytes_per_pixel >= 2 {
                            Self::write_byte(
                                buffer,
                                offset + 1,
                                green,
                            );
                        }

                        if bytes_per_pixel >= 3 {
                            Self::write_byte(
                                buffer,
                                offset + 2,
                                blue,
                            );
                        }
                    }

                    PixelFormat::U8 => {
                        Self::write_byte(
                            buffer,
                            offset,
                            red,
                        );
                    }

                    PixelFormat::Unknown { .. } => {
                        // Unknown framebuffer format.
                        // Do not attempt to interpret the pixel layout.
                    }

                    _ => {
                        // Future PixelFormat variants.
                    }
                }
            }
        }
    }

    fn write_byte(
        buffer: &mut [u8],
        offset: usize,
        value: u8,
    ) {
        if offset < buffer.len() {
            unsafe {
                core::ptr::write_volatile(
                    buffer.as_mut_ptr().add(offset),
                    value,
                );
            }
        }
    }
}