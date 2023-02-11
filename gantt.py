from datetime import date,datetime,timedelta

from dataclasses import dataclass
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from pandas import Timestamp
import csv
from pprint import pprint

COLORS = ['#34D05C',
          '#E64646',
          '#34D0C3',
          '#E69646',
          '#3475D0']

BG_COLOR= '#36454F'


@dataclass
class Task:
    label : str
    phase : str
    start: date
    end : date
    completion : float

    def __str__(self):
        return f"{self.label} ({self.phase}): du {self.start} to {self.end} [{self.completion*100} %]"

    @property
    def duration(self):
        return (self.end-self.start).days

    def progression_in_days(self):
        return self.duration * self.completion

class Project():
    """
    Implements a project with tasks
    """
    def __init__(self,tasks:list[Task],title=""):
        self.tasks = sorted(tasks,key=lambda x:x.start,reverse=True)
        self.title = title

    @property
    def start_date(self):
        return min([t.start for t in self.tasks])

    @property
    def end_date(self):
        return max([t.end for t in self.tasks])

    def __iter__(self):
        return iter(self.tasks)

    def nb_days_from_start(self,event:Task|date):
        if isinstance(event,Task):
            date_event = event.start
        else:
            date_event = event
        return (date_event - self.start_date).days
    
    def nb_days_until_end(self,task:Task):
        return (self.end_date - task.end).days
    @property
    def phases(self):
        return set([t.phase for t in self.tasks])
    @property
    def duration(self):
        return (self.end_date - self.start_date).days
    

def plot_gantt(project:Project, export_filename:str=None):
    """
    
    Plot project as a gantt diagram

    Paremeters
    ------------
    project:Project
    project to plot

    export_filename:str
    Filename where to export the gantt. If None, displayed to screen
    
    Notes
    ------------
    Adapted from https://towardsdatascience.com/gantt-charts-with-pythons-matplotlib-395b7af72d72
    https://gist.github.com/Thiagobc23/fc12c3c69fbb90ac64b594f2c3641fcf
    """
    
    # color initialization
    color_phases = {phase:COLORS[i%len(COLORS)] for i,phase in enumerate(project.phases)}

    fig, (ax, ax1) = plt.subplots(2, figsize=(16,6), gridspec_kw={'height_ratios':[6, 1]}, facecolor=BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    ax1.set_facecolor(BG_COLOR)

    #plot tasks
    for i,t in enumerate(project):
        ax.barh(t.label, t.progression_in_days(),
                left=project.nb_days_from_start(t),
                color=color_phases[t.phase])
        ax.barh(t.label,
                t.duration,
                left=project.nb_days_from_start(t),
                color=color_phases[t.phase], alpha=0.5)
        ax.text(project.duration-project.nb_days_until_end(t)+0.1, i, f"{int(t.completion*100)}%", va='center', alpha=0.8, color='w')
        ax.text(project.nb_days_from_start(t)-0.1, i, t.label, va='center', ha='right', alpha=0.8, color='w')

    # grid lines
    ax.set_axisbelow(True)
    ax.xaxis.grid(color='k', linestyle='dashed', alpha=0.4, which='both')

    # ticks
    xticks_minor = list(range(0,project.duration+1, project.duration//30))
    xticks = xticks_minor[::3]
    xticks_labels = [(project.start_date+timedelta(days=d)).strftime("%d/%m") for d in xticks]
    ax.set_xticks(xticks)
    ax.set_xticks(xticks_minor, minor=True)
    ax.set_xticklabels(xticks_labels, color='w')
    ax.set_yticks([])
    plt.setp([ax.get_xticklines()], color='w')

    # align x axis
    ax.set_xlim(0, project.duration)

    # remove spines
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['left'].set_position(('outward', 10))
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_color('w')



    plt.suptitle(project.title, color='w')
    ##### LEGENDS #####
    # TODO : à faire autrement ?
    legend_elements = [Patch(facecolor=color, label=phase) for phase,color in color_phases.items()]
    legend = ax1.legend(handles=legend_elements, loc='upper center', ncol=len(legend_elements), frameon=False)
    plt.setp(legend.get_texts(), color='w')

    # clean second axis
    ax1.spines['right'].set_visible(False)
    ax1.spines['left'].set_visible(False)
    ax1.spines['top'].set_visible(False)
    ax1.spines['bottom'].set_visible(False)
    ax1.set_xticks([])
    ax1.set_yticks([])

    # add a line to see current day
    current_date = datetime.now().date()
    ax.axvline(x = project.nb_days_from_start(current_date), color = 'r', label = 'axvline - full height')
    if export_filename is None:
        plt.show()
    else:
        plt.savefig(export_filename, facecolor=BG_COLOR)

    

def read_gantt(filename:str):
    """
    Returns a list of Task read from csv file filename
    check gantt.csv for columns names
    """
    data = []
    with open(filename,"r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            start = datetime.strptime(row['start'],'%d/%m/%y').date()
            end = datetime.strptime(row['end'],'%d/%m/%y').date()
            completion = float(row['completion'])
            task = Task(row['task'],row['phase'],start,end,completion)
            data.append(task)
    return data


if __name__ == "__main__":
    data = read_gantt('gantt.csv')
    project = Project(data,"HDR")
    plot_gantt(project)
        
    
