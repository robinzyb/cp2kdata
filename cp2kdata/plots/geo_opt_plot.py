import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import os


def geo_opt_info_plot(geo_opt_info, dst):
    plt.rcParams.update(
        {
            'font.size': 20,
            'axes.linewidth': 2,
            'lines.marker': 'o',
            'lines.markeredgecolor': 'black',
            'lines.markeredgewidth': '0.5',
            'lines.markersize': 13,
            'xtick.major.size': 5,
            'xtick.major.width': 2,
            'ytick.major.width': 2
        }
    )
    geo_opt_steps = [one_geo_opt_info["step"]
                     for one_geo_opt_info in geo_opt_info()[1:]]
    max_step_size = [one_geo_opt_info["max_step_size"]
                     for one_geo_opt_info in geo_opt_info()[1:]]
    rms_step_size = [one_geo_opt_info["rms_step_size"]
                     for one_geo_opt_info in geo_opt_info()[1:]]
    max_grad = [one_geo_opt_info["max_gradient"]
                for one_geo_opt_info in geo_opt_info()[1:]]
    rms_grad = [one_geo_opt_info["rms_gradient"]
                for one_geo_opt_info in geo_opt_info()[1:]]

    fig = plt.figure(figsize=(24, 16), dpi=300)

    gs = GridSpec(2, 2, figure=fig)
    color = 'black'
    ax_max_step = fig.add_subplot(gs[0])
    ax_max_step.plot(geo_opt_steps, max_step_size,
                     color=color, markerfacecolor="#F2F2F2")
    ax_max_step.set_ylabel("Max Step Size")
    ax_max_step.set_xlabel("Optimzation Steps")
    ax_max_step.set_yscale('log')
    ax_max_step.hlines(geo_opt_info(
    )[-1]["limit_step_size"], 0, geo_opt_steps[-1], color='lightcoral', ls='dashed')
    ax_rms_step = fig.add_subplot(gs[1])
    ax_rms_step.plot(geo_opt_steps, rms_step_size,
                     color=color, markerfacecolor="#C6E070")
    ax_rms_step.set_ylabel("RMS Step Size")
    ax_rms_step.set_xlabel("Optimzation Steps")
    ax_rms_step.set_yscale('log')
    ax_rms_step.hlines(geo_opt_info(
    )[-1]["limit_rms_step"], 0, geo_opt_steps[-1], color='lightcoral', ls='dashed')
    ax_max_grad = fig.add_subplot(gs[2])
    ax_max_grad.plot(geo_opt_steps, max_grad, color=color,
                     markerfacecolor="#91C46C")
    ax_max_grad.set_xlabel("Optimzation Steps")
    ax_max_grad.set_ylabel("Max Gradient")
    ax_max_grad.set_yscale('log')
    ax_max_grad.hlines(geo_opt_info(
    )[-1]["limit_gradient"], 0, geo_opt_steps[-1], color='lightcoral', ls='dashed')
    ax_rms_grad = fig.add_subplot(gs[3])
    ax_rms_grad.plot(geo_opt_steps, rms_grad, color=color,
                     markerfacecolor="#5C832F")
    ax_rms_grad.set_ylabel("RMS Gradient")
    ax_rms_grad.set_xlabel("Optimzation Steps")
    ax_rms_grad.set_yscale('log')
    ax_rms_grad.hlines(geo_opt_info(
    )[-1]["limit_rms_gradient"], 0, geo_opt_steps[-1], color='lightcoral', ls='dashed')
    fig.suptitle("Geometry Optimization Information", fontsize=30)
    fig.tight_layout()
    fig.savefig(os.path.join(dst, "geo_opt_info.png"))
