import itertools as it

import numpy as np
from qiskit_experiments.data_processing import SkLDA
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from uncertainties import unumpy as unp


def signal(x, std_dev_decay=100, phase=0, decay=10):
    """Arbitrary decaying sinusoidal signal."""
    return unp.uarray(
        np.sin(x + phase) * np.exp(-x / decay),
        1.1 - np.exp(-x / std_dev_decay),
    )


def generate_data():
    """Generate dummy curve-data for CurvePlotter."""
    data = {}
    for series, phase, decay in zip(
        ["A", "B", "C", "D"], [0, np.pi / 3, 0, np.pi / 3], [10, 10, 1e9, 1e9]
    ):
        series_data = {}
        series_data = {
            "x": np.linspace(0, 20, 20),
            "x_interp": np.linspace(0, 20, 200),
        }
        series_data.update(
            {
                "y": unp.nominal_values(
                    signal(series_data["x"], decay=decay, phase=phase)
                ),
                "y_interp": signal(series_data["x_interp"], decay=decay, phase=phase),
            }
        )
        series_data.update(
            {
                "y_interp_err": unp.std_devs(series_data["y_interp"]) ** 2,
                "y_interp": unp.nominal_values(series_data["y_interp"]),
            }
        )
        if series == "C" or series == "C":
            series_data = {
                "x": series_data["x"],
                "y": series_data["y"],
                "x_interp": series_data["x_interp"],
                "y_interp": series_data["y_interp"],
            }
        data[series] = series_data
    return data


def generate_iq_data(
    centres=[(8, 8), (-6.4, 1.6), (-2, 1.1)],
    sigmas=[1, 1, 1],
    n_points=4096,
    n_relaxation=256,
):
    """Generate dummy IQ data, including a discriminator, for IQPlotter."""
    data = {}
    for state, centre, sigma in zip(["0", "1", "2"], centres, sigmas):
        points_I = np.random.normal(centre[0], sigma, n_points)
        points_Q = np.random.normal(centre[1], sigma, n_points)
        points = np.concatenate(
            [points_I.reshape((-1, 1)), points_Q.reshape((-1, 1))], axis=1
        )

        # Handle relaxation
        if state == "1":
            points[0:n_relaxation] = data["0"]["points"][0:n_relaxation]

        centroid = np.mean(points,axis=0)
        series = state
        data[series] = {
            "points": points,
            "centroid": centroid,
        }
    # Create and train linear discriminator
    lda = LinearDiscriminantAnalysis()
    sklda = SkLDA(lda)
    sklda.fit(
        np.concatenate([d["points"] for _, d in data.items()]),
        np.asarray([[f"{l}"] * n_points for l in data.keys()]).flatten().transpose(),
    )
    return data, sklda
