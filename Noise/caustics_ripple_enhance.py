import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import imageio
import os

phase_const = .57 #.3

def ripple_interference(shape=(512, 512), wave_count=5, seed=None, phase_shift=0.0):
    if seed is not None:
        np.random.seed(seed)
    ny, nx = shape
    y, x = np.mgrid[0:ny, 0:nx] / ny

    result = np.zeros_like(x, dtype=float)
    for _ in range(wave_count):
        angle = np.random.uniform(0, 2*np.pi)
        freq = np.random.uniform(6, 15) #4,12
        phase = np.random.uniform(0, 2*np.pi) + phase_shift
        result += np.sin(np.cos(angle)*x*freq + np.sin(angle)*y*freq + phase)
    result -= result.min()
    result /= result.max()
    return result


def caustic_enhance(field, gamma=2.5, boost=2.5):
    enhanced = np.power(field, gamma) * boost
    enhanced = np.clip(enhanced, 0, 1)
    return enhanced


blue_black_white = LinearSegmentedColormap.from_list("caustics", [
        (0.0, "#001f3f"),
        (0.4, "#0074D9"),
        (0.9, "#7FDBFF"),
        (1.0, "#ffffff")
    ])

orange_yellow_red_white = LinearSegmentedColormap.from_list("caustics", [
        (0.0, "#800080"),
        (0.4, "#FFFF00"),
        (0.9, "#FFA500"),
        (1.0, "#000000")
    ])

orange_yellow_red_blue = LinearSegmentedColormap.from_list("caustics", [
        (0.0, "#800080"),
        (0.4, "#FFFF00"),
        (0.9, "#FFA500"),
        (1.0, "#00FFFF")
    ])

def caustic_cmap():
    return blue_black_white


def save_image(array, filename="caustics.png", cmap="plasma"):
    plt.imsave(filename, array, cmap=cmap)


def generate_gif(frame_count=300, shape=(512, 512), output="caustics.gif",
                 cmap="plasma", duration=0.1, seed=None):
    frames = []
    for i in range(frame_count):
        phase = i * phase_const
        img = ripple_interference(shape, wave_count=7, seed=seed, phase_shift=phase)
        enhanced = caustic_enhance(img, gamma=2.8, boost=3.0)

        fig, ax = plt.subplots(figsize=(shape[1] / 100, shape[0] / 100), dpi=100)
        ax.axis('off')
        ax.imshow(enhanced, cmap=cmap)

        temp_file = f"_temp_frame_{i}.png"
        plt.savefig(temp_file, bbox_inches='tight', pad_inches=0)
        plt.close(fig)
        frames.append(imageio.v2.imread(temp_file))
        os.remove(temp_file)

    imageio.mimsave(output, frames, duration=duration)


if __name__ == "__main__":
    shape = (512, 512)
    base = ripple_interference(shape, wave_count=7, seed=78)
    enhanced = caustic_enhance(base, gamma=2.3, boost=2.4)#caustic_enhance(base, gamma=2.8, boost=3.0)
    save_image(enhanced, filename="caustics_static6.png", cmap=caustic_cmap())

    generate_gif(frame_count=100, shape=(2048, 2048), output="caustics_animated6.gif",
                 cmap=caustic_cmap(), duration=0.8, seed=78)
