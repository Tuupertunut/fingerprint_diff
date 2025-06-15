import subprocess
import numpy as np
import matplotlib.pyplot as plt
import sys
import os


def get_fingerprint(file_path):
    """Run fpcalc and return the fingerprint as a list of integers."""
    try:
        result = subprocess.run(
            ["fpcalc", "-raw", "-length", "120", file_path],
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"Error processing file {file_path}: {e}")
        return None

    for line in result.stdout.splitlines():
        if line.startswith("FINGERPRINT="):
            fingerprint_str = line.strip().split("=", 1)[1]
            return list(map(int, fingerprint_str.split(",")))
    return None


def int_to_bits(n, width=32):
    """Convert integer to a list of bits (LSB to MSB)."""
    return [(n >> i) & 1 for i in range(width)]


def compute_bitwise_diff(fp1, fp2):
    """Compute bitwise XOR difference matrix between two fingerprint arrays."""
    max_len = max(len(fp1), len(fp2))
    fp1 += [0] * (max_len - len(fp1))
    fp2 += [0] * (max_len - len(fp2))

    diff_matrix = []

    for a, b in zip(fp1, fp2):
        xor = a ^ b
        bits = int_to_bits(xor)
        diff_matrix.append(bits)

    # Transpose so bits are on Y axis, time/frame on X axis
    return np.array(diff_matrix).T


def plot_bitwise_diff(fp1_bits, fp2_bits, bit_diff, output_path):
    """Plot and save bitwise difference heatmap."""
    fig, axs = plt.subplots(3, figsize=(16, 9), sharex=True)

    axs[0].imshow(
        fp1_bits,
        cmap="Greys",
        aspect="auto",
        interpolation="nearest",
        origin="lower",
        vmin=0,
        vmax=1,
    )
    axs[0].set_ylabel("Bit Position (0 = LSB, 31 = MSB)")
    axs[0].set_title("Chromaprint Fingerprint 1 (white=0, black=1)")

    axs[1].imshow(
        fp2_bits,
        cmap="Greys",
        aspect="auto",
        interpolation="nearest",
        origin="lower",
        vmin=0,
        vmax=1,
    )
    axs[1].set_ylabel("Bit Position (0 = LSB, 31 = MSB)")
    axs[1].set_title("Chromaprint Fingerprint 2 (white=0, black=1)")

    axs[2].imshow(
        bit_diff,
        cmap="Greys",
        aspect="auto",
        interpolation="nearest",
        origin="lower",
        vmin=0,
        vmax=1,
    )
    axs[2].set_xlabel("Fingerprint Frame")
    axs[2].set_ylabel("Bit Position (0 = LSB, 31 = MSB)")
    axs[2].set_title(
        "Bitwise Chromaprint Fingerprint Difference (white=same, black=different), Total: "
        + str(np.count_nonzero(bit_diff))
        + " bits differ"
    )

    fig.tight_layout()
    if output_path is None:
        plt.show()
    else:
        fig.savefig(output_path)


def main(file1, file2, output_path=None):
    if not os.path.isfile(file1) or not os.path.isfile(file2):
        print("One or both audio files do not exist.")
        return

    print(f"Generating fingerprints for:\n  - {file1}\n  - {file2}")
    fp1 = get_fingerprint(file1)
    fp2 = get_fingerprint(file2)

    if fp1 is None or fp2 is None:
        print("Failed to extract fingerprints.")
        return

    bit_diff = compute_bitwise_diff(fp1, fp2)
    fp1_bits = np.array([int_to_bits(n) for n in fp1]).T
    fp2_bits = np.array([int_to_bits(n) for n in fp2]).T
    plot_bitwise_diff(fp1_bits, fp2_bits, bit_diff, output_path)


if __name__ == "__main__":
    if len(sys.argv) == 3:
        main(sys.argv[1], sys.argv[2])
    elif len(sys.argv) == 4:
        main(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        print("Usage: " + sys.argv[0] + " audio1.wav audio2.wav [plot.png]")
