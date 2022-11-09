![Tests](https://github.com/joew5887/FPL-Player/actions/workflows/tests.yml/badge.svg)

# FPL-Player

## What is it?
API wrapper for Fantasy Premier League Football (FPL) in Python.

Get information about teams, players, fixtures, and gameweeks in package `fpld`.

To come: Predictor for FPL points.

I do not own any of the data. It is available at "https://fantasy.premierleague.com/api/".

## Requirements
* Requires Python 3.10 (Tested on 3.10.4)
* Only tested on Windows

## Installation
Run these two commands:
1. `git clone https://github.com/joew5887/FPL-Player.git`
2. `python setup.py install`

## Example
```
teams = fpld.Team.get_all()

labels = [team.short_name for team in teams]
gk_points = [sum([p.total_points for p in team.players_by_pos(
    fpld.Position.get_by_id(1))]) for team in teams]
def_points = [sum([p.total_points for p in team.players_by_pos(
    fpld.Position.get_by_id(2))]) for team in teams]
mid_points = [sum([p.total_points for p in team.players_by_pos(
    fpld.Position.get_by_id(3))]) for team in teams]
fwd_points = [sum([p.total_points for p in team.players_by_pos(
    fpld.Position.get_by_id(4))]) for team in teams]

labels_x = np.arange(len(labels))

fig, ax = plt.subplots()
width = 0.1

rects1 = ax.bar(labels_x - (3 / 2) * width,
                gk_points, width, label="GK")
rects2 = ax.bar(labels_x - (1 / 2) * width, def_points, width,label="DEF")
rects3 = ax.bar(labels_x + (1 / 2) * width, mid_points, width,label="MID")
rects4 = ax.bar(labels_x + (3 / 2) * width,
                fwd_points, width, label="FWD")

ax.set_ylabel("Total Points")
ax.set_title("Team total points by position")
ax.set_xticks(labels_x, labels)
ax.legend()

ax.bar_label(rects1, padding=3)
ax.bar_label(rects2, padding=3)
ax.bar_label(rects3, padding=3)
ax.bar_label(rects4, padding=3)

fig.tight_layout()
plt.show()
```

Outputs

![Graph](graph.png)