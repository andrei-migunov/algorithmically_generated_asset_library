import numpy as np
import matplotlib.pyplot as plt
from scipy.fftpack import fft2, ifft2, fftshift
import imageio
from PIL import Image
import os


def generate_pink_noise(shape=(512, 512), octaves=8, seed=None):
    if seed is not None:
        np.random.seed(seed)

    def f_filter(shape):
        ny, nx = shape
        y = np.fft.fftfreq(ny)[:, None]
        x = np.fft.fftfreq(nx)[None, :]
        radius = np.sqrt(x * x + y * y)
        radius[radius == 0] = 1  # Avoid divide-by-zero
        return 1.0 / np.power(radius, 0.5)  # pink noise ~ 1/f^0.5

    white = np.random.randn(*shape)
    f = fft2(white)
    f = fftshift(f) * f_filter(shape)
    f = fftshift(f)
    pink = np.real(ifft2(f))

    pink -= pink.min()
    pink /= pink.max()
    return pink


def save_image(array, filename="pink_noise.png", cmap="plasma"):
    plt.imsave(filename, array, cmap=cmap)


def generate_gif(frame_count=30, shape=(512, 512), output="pink_noise.gif",
                 cmap="plasma", duration=0.1, seed=None):
    frames = []
    for i in range(frame_count):
        frame_seed = None if seed is None else seed + i
        img = generate_pink_noise(shape, seed=frame_seed)

        fig, ax = plt.subplots(figsize=(shape[1] / 100, shape[0] / 100), dpi=100)
        ax.axis('off')
        ax.imshow(img, cmap=cmap)

        temp_file = f"_temp_frame_{i}.png"
        plt.savefig(temp_file, bbox_inches='tight', pad_inches=0)
        plt.close(fig)
        frames.append(imageio.v2.imread(temp_file))
        os.remove(temp_file)

    imageio.mimsave(output, frames, duration=duration)


# Example usage:
if __name__ == "__main__":
    # Single image
    noise = generate_pink_noise(shape=(512, 512), seed=42)
    save_image(noise, filename="pink_noise.png", cmap="viridis")

    # Animated GIF
    generate_gif(frame_count=20, shape=(256, 256), output="animated_pink.gif",
                 cmap="magma", duration=0.15, seed=42)