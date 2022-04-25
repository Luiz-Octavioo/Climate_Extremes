# Function for plot KDE
import pandas as pd


def plot_kde(df, label, color, ax, **kwargs):
    """
    Plot KDE
    """
    df.plot.kde(label=label, color=color, ax=ax, **kwargs)

