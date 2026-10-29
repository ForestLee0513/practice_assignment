"""저장된 학습률별 CSV를 읽어 가중치와 손실 비교 그래프를 저장합니다."""
from pathlib import Path
import csv

import matplotlib

matplotlib.use("Agg")  # GUI 없이도 이미지 파일로 저장
import matplotlib.pyplot as plt


def main():
    output_dir = Path(__file__).resolve().parent / "outputs"
    fig, axes = plt.subplots(1, 3, figsize=(16, 5), constrained_layout=True)
    descriptions = {"0.01": "Slow change", "0.1": "Steady approach",
                    "0.8": "Oscillating convergence"}

    for lr in ("0.01", "0.1", "0.8"):
        with (output_dir / f"updates-{lr}.csv").open(
            encoding="utf-8-sig", newline=""
        ) as file:
            rows = list(csv.DictReader(file))

        steps = [int(row["step"]) for row in rows]
        weights = [float(row["w_after"]) for row in rows]
        losses = [float(row["loss_after"]) for row in rows]
        # CSV는 갱신 이후 값만 기록하므로 초기값을 step 0으로 추가합니다.
        initial_weight = float(rows[0]["w_before"])
        axes[0].plot([0] + steps, [initial_weight] + weights,
                     marker="o", label=f"lr={lr}: {descriptions[lr]}")
        axes[1].plot([0] + steps, [initial_weight - 4] + [w - 4 for w in weights],
                     marker="o", label=f"lr={lr}")
        axes[2].semilogy([0] + steps, [(initial_weight - 4) ** 2] + losses,
                         marker="o", label=f"lr={lr}")

    axes[0].axhline(4, color="gray", linestyle="--", label="Target w=4")
    axes[0].set(title="Slow change vs. iteration count", xlabel="Iteration",
                ylabel="Weight (w)")
    axes[1].axhline(0, color="gray", linestyle="--", label="Target error=0")
    axes[1].set(title="Oscillation: crossing the target", xlabel="Iteration",
                ylabel="Signed error (w - 4)")
    axes[2].set(title="Loss reduction vs. iteration count", xlabel="Iteration",
                ylabel="Loss: (w - 4)^2")
    for ax in axes:
        ax.set_xticks(range(11))
        ax.grid(True, which="both", alpha=0.3)
        ax.legend()
    fig.suptitle("Learning rate: slow change, oscillation, and iterations (CSV: 1-10)")
    for extension in ("png", "svg"):
        destination = output_dir / f"learning_rate_comparison.{extension}"
        fig.savefig(destination, dpi=180)
        print(f"Saved: {destination}")
    plt.close(fig)


if __name__ == "__main__":
    main()
