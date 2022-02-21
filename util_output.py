"""
output utilities
"""

from typing import *

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from util import *

DEBUGGING = True
if DEBUGGING:
    pd.set_option("display.max_columns", None)
    np.set_printoptions(linewidth=200, precision=3)

###########################
# matplotlib options
###########################
plt.rcParams['figure.figsize'] = (18.0, 9.0)
# plt.rcParams["font.family"] = 'Times'
plt.rcParams["font.size"] = 9
fig = plt.figure(dpi=200)
color_value = {
    '0': 'midnightblue',
    '1': 'mediumblue',
    '2': 'c',
    '3': 'orangered',
    '4': 'm',
    '5': 'fuchsia',
    '6': 'olive'
}

###########################
# output format
###########################
COLUMNS_CHS_ENG = {
    '车次': 'id',
    '站序': 'station#',
    '站名': 'station_name',
    '到点': 'str_time_arr',
    '发点': 'str_time_dep'
}


def read_timetable_csv(fpath, st=None, station_name_map=None):
    """

    read standard timetable csv

    Args:
        fpath: file path
        st:    start-time of the timetable.
            if not defined, infer from the data.

    Returns:
    """
    df = pd.read_excel(fpath).rename(
        columns=COLUMNS_CHS_ENG
    ).assign(
        station_id=lambda df: df['station_name'].apply(station_name_map.get),
        station_i=lambda df: df['station_id'].apply(lambda x: f"_{x}"),
        station_o=lambda df: df['station_id'].apply(lambda x: f"{x}_"),
        time_arr=lambda df: pd.to_datetime(df['str_time_arr']).apply(lambda x: x.hour * 60 + x.minute - st),
        time_dep=lambda df: pd.to_datetime(df['str_time_dep']).apply(lambda x: x.hour * 60 + x.minute - st)
    )
    train_paths = df.groupby('id').apply(
        lambda grp: sorted(
            list(zip(grp['station_i'], grp['time_arr'])) + list(zip(grp['station_o'], grp['time_dep'])),
            key=lambda x: x[-1]
        )
    )
    return df, train_paths


def plot_timetables_h5(train_list, miles, station_list, param_sys: SysParams, param_subgrad: SubgradParam,
                       selective: List = None):
    import plotly.graph_objects as go

    fig = go.Figure()

    plotted = []
    universe = [tr.traNo for tr in train_list]
    for i in range(len(train_list)):
        train = train_list[i]
        if selective is not None and train.traNo not in selective:
            continue
        xlist = []
        ylist = []
        if not train.is_best_feasible:
            continue
        for sta_id in range(len(train.staList)):
            sta = train.staList[sta_id]
            if sta_id != 0:  # 不为首站, 有到达
                if "_" + sta in train.v_staList:
                    xlist.append(train.timetable["_" + sta])
                    ylist.append(miles[station_list.index(sta)])
            if sta_id != len(train.staList) - 1:  # 不为末站，有出发
                if sta + "_" in train.v_staList:
                    xlist.append(train.timetable[sta + "_"])
                    ylist.append(miles[station_list.index(sta)])
        fig.add_scatter(
            mode='lines+markers',
            x=xlist, y=ylist,
            line={"dash": "solid"},
            name=f"train-{train.traNo}:{train.speed}",
        )
        plotted.append(train.traNo)

    unplotted = set(universe).difference(plotted)
    fig.update_layout(
        title=f"Best primal solution of # trains, station, periods: ({len(train_list)}, {param_sys.station_size}, {param_sys.time_span})\n"
              f"Number of trains {param_subgrad.max_number} \n"
              f"Failed: {len(unplotted)}"
    )
    fig.update_xaxes(title="minutes",
                     tickvals=np.arange(0, param_sys.time_span, param_sys.time_span / 30).round(2))
    fig.update_yaxes(title="miles",
                     tickvals=miles)

    fig.write_html(
        f"{param_sys.fdir_result}/{param_subgrad.dual_method}.{param_subgrad.feasible_provider}@{param_subgrad.iter}-{param_sys.train_size}.{param_sys.station_size}.{param_sys.time_span}.html",
    )


def plot_timetables(train_list, miles, station_list, param_sys: SysParams, param_subgrad: SubgradParam,
                    selective: List = None):
    for i in range(len(train_list)):
        train = train_list[i]
        if selective is not None and train.traNo not in selective:
            continue
        xlist = []
        ylist = []
        if not train.is_best_feasible:
            continue
        for sta_id in range(len(train.staList)):
            sta = train.staList[sta_id]
            if sta_id != 0:  # 不为首站, 有到达
                if "_" + sta in train.v_staList:
                    xlist.append(train.timetable["_" + sta])
                    ylist.append(miles[station_list.index(sta)])
            if sta_id != len(train.staList) - 1:  # 不为末站，有出发
                if sta + "_" in train.v_staList:
                    xlist.append(train.timetable[sta + "_"])
                    ylist.append(miles[station_list.index(sta)])
        plt.plot(xlist, ylist, color=color_value[str(i % 7)], linewidth=1.5)
        plt.text(xlist[0] + 0.8, ylist[0] + 4, train.traNo, ha='center', va='bottom',
                 color=color_value[str(i % 7)], weight='bold', family='Times', fontsize=9)

    plt.grid(True)  # show the grid
    plt.ylim(0, miles[-1])  # y range

    plt.xlim(0, param_sys.time_span)  # x range
    sticks = 20
    plt.xticks(np.linspace(0, param_sys.time_span, sticks))

    plt.yticks(miles, station_list, family='Times')
    plt.xlabel('Time (min)', family='Times new roman')
    plt.ylabel('Space (km)', family='Times new roman')
    plt.title(
        f"Best primal solution of # trains, station, periods: ({len(train_list)}, {param_sys.station_size}, {param_sys.time_span})\n"
        f"Number of trains {param_subgrad.max_number}", fontdict={"weight": 500, "size": 20})

    plt.savefig(
        f"{param_sys.fdir_result}/{param_subgrad.dual_method}.{param_subgrad.feasible_provider}@{param_subgrad.iter}-{param_sys.train_size}.{param_sys.station_size}.{param_sys.time_span}.png",
        dpi=500)
    plt.clf()


def plot_convergence(param_sys: SysParams, param_subgrad: SubgradParam):
    ## plot the bound updates
    font_dic = {
        "family": "Times",
        "style": "oblique",
        "weight": "normal",
        "color": "green",
        "size": 20
    }

    x_cor = range(0, param_subgrad.iter + 1)
    plt.plot(x_cor, param_subgrad.lb_arr, label='LB')
    plt.plot(x_cor, param_subgrad.ub_arr, label='UB')
    plt.legend()
    plt.xlabel('Iteration', fontdict=font_dic)
    plt.ylabel('Bounds update', fontdict=font_dic)
    plt.title('LR: Bounds updates \n', fontsize=23)
    plt.savefig(
        f"{param_sys.fdir_result}/{param_subgrad.dual_method}.{param_subgrad.primal_heuristic_method}-{param_sys.train_size}.{param_sys.station_size}.{param_sys.time_span}.convergence.png",
        dpi=500)
    plt.clf()
