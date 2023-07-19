#!/usr/bin/env python3

# Copyright (C) 2021-2023 Guillaume Jouvet <guillaume.jouvet@unil.ch>
# Published under the GNU GPL (Version 3), check at the LICENSE file 

import numpy as np
import os, sys, shutil
import matplotlib.pyplot as plt
import matplotlib
import datetime, time
import tensorflow as tf

from igm.modules.utils import *

def params_write_plot2d(parser):
    parser.add_argument(
        "--editor_plot2d",
        type=str,
        default="vs",
        help="optimized for VS code (vs) or spyder (sp) for live plot",
    )
    parser.add_argument(
        "--plot_live",
        type=str2bool,
        default=False,
        help="Display plots live the results during computation (Default: False)",
    )
    parser.add_argument(
        "--plot_particles",
        type=str2bool,
        default=True,
        help="Display particles (Default: True)",
    )
    parser.add_argument(
        "--varplot",
        type=str,
        default="velbar_mag",
        help="variable to plot",
    )
    parser.add_argument(
        "--varplot_max",
        type=float,
        default=250,
        help="maximum value of the varplot variable used to adjust the scaling of the colorbar",
    )


def init_write_plot2d(params, state):
    state.extent = [np.min(state.x), np.max(state.x), np.min(state.y), np.max(state.y)]

    if params.editor_plot2d == "vs":
        plt.ion() # enable interactive mode

    state.tcomp_write_plot2d = []

    state.fig = plt.figure(dpi=200)
    state.ax = state.fig.add_subplot(1, 1, 1)
    state.ax.axis("off")
    state.ax.set_aspect("equal")

    os.system(
        "echo rm "
        + os.path.join(params.working_dir, params.varplot + "*.png")
        + " >> clean.sh"
    )


def update_write_plot2d(params, state):

    if state.saveresult:
 
        state.tcomp_write_plot2d.append(time.time())

        if params.varplot == "velbar_mag":
            state.velbar_mag = getmag(state.ubar, state.vbar)
 
        im0 = state.ax.imshow(
            state.topg,
            origin="lower",
            cmap=matplotlib.cm.terrain,
            extent=state.extent,
            alpha=0.65
        )

        im = state.ax.imshow(
            np.where(state.thk>0, vars(state)[params.varplot],np.nan),
            origin="lower",
            cmap=matplotlib.cm.viridis,
            vmin=0,
            vmax=params.varplot_max,
            extent=state.extent
        )
        if params.plot_particles:
            if hasattr(state, "xpos"):
                if hasattr(state, "ip"):
                    state.ip.set_visible(False)
                r = 1
                state.ip = state.ax.scatter(
                    x=state.xpos[::r],
                    y=state.ypos[::r],
                    c=1 - state.rhpos[::r].numpy(),
                    vmin=0,
                    vmax=1,
                    s=0.5,
                    cmap="RdBu",
                )
        state.ax.set_title("YEAR : " + str(state.t.numpy()), size=15)

        if not hasattr(state,'already_set_cbar'):
                state.cbar = plt.colorbar(im, label=params.varplot)
                state.already_set_cbar = True

        if params.plot_live:
            if params.editor_plot2d == "vs":
                state.fig.canvas.draw()         # re-drawing the figure
                state.fig.canvas.flush_events() # to flush the GUI events
            else:
                from IPython.display import display, clear_output
                clear_output(wait=True)
                display(state.fig)
        else:
            plt.savefig(
                os.path.join(
                    params.working_dir,
                    params.varplot + "-" + str(state.t.numpy()).zfill(4) + ".png",
                ),
                bbox_inches="tight",
                pad_inches=0.2,
            )

        state.tcomp_write_plot2d[-1] -= time.time()
        state.tcomp_write_plot2d[-1] *= -1


def final_write_plot2d(params, state):
    pass