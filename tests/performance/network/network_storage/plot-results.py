#  Copyright (c) 2014 John Biddiscombe
#
#  Distributed under the Boost Software License, Version 1.0. (See accompanying
#  file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)

#!/usr/bin/python
import optparse
import itertools
from StringIO import StringIO
import csv
import os
import re
import glob
import math
import numpy
from numpy import array
import matplotlib

workdir = os.getcwd()

#----------------------------------------------------------------------------
# Arguments and help
parser = optparse.OptionParser()
parser.add_option("--fig-size", type = "string", default = None)
parser.add_option("--show", action = "store_true", dest = "show_graph", default = False)
parser.add_option("--verbose", action = "store_true", default = False)
parser.add_option("--quiet", action = "store_true", default = False)
parser.add_option("--title", action = "store", dest = "title", default = False)

options, args = parser.parse_args();

#----------------------------------------------------------------------------
# convenience definitions to loop over all marker/colour styles 
# when we have a lot of lines on the same graph
colors=itertools.cycle(('r','g','b','c','y','m','k'))
marker=itertools.cycle(('+', '.', 'o', '*', '^', 's', 'v', ',', '<', '>', '8', 's', 'p', 'h', 'H', 'D', 'd')) 
filled_markers = itertools.cycle(('o', 'v', '^', '<', '>', '8', 's', 'p', '*', 'h', 'H', 'D', 'd'))
#----------------------------------------------------------------------------

if (not options.show_graph) :
    matplotlib.use('SVG')
# this import must come after the use() call above    
import matplotlib.pyplot as plt

#----------------------------------------------------------------------------
# setup default size of plot if user didn't pass fig_size command line option
try :
    size = map(float, options.fig_size.split())
    if len(size) == 2 :
        options.fig_size = (size, [0.1, 0.1, 0.85, 0.85])
    elif len(size) == 6 :
        options.fig_size = (size[0:2], size[2:6])
    else :
        raise ValueError("--fig-size must be a string of 2 of 6 numbers")
except :
    options.fig_size = ([12, 9], [0.08, 0.14, 0.91, 0.83])
#    options.fig_size = ([6, 8], [0.16, 0.22, 0.79, 0.77])

#----------------------------------------------------------------------------
def maximum(iterable, default):
    '''Like max(), but returns a default value if xs is empty.'''
    try:
        return max(iterable)
    except ValueError:
         return default

#----------------------------------------------------------------------------
def minimum(iterable, default):
    '''Like min(), but returns a default value if xs is empty.'''
    try:
        return min(iterable)
    except ValueError:
         return default
         
#----------------------------------------------------------------------------
def sizeof_fmt(num):
    for x in ['bytes','KB','MB','GB','TB']:
        if num < 1024.0:
            return "%.0f %s" % (num, x)
        num /= 1024.0      
#----------------------------------------------------------------------------
#
# plot N series of data onto a single graph
# each series is a array, there are N arrays in the supplied map 
# graph_map, a map of arrays of {x,y,other} data
# labels, {xaxis, yaxis, series_variable} 
def plot_one_collection(graph_map, labelstrings, axes) :
    print "Plotting %i graphs of '%s'" % (len(graph_map), labelstrings[2])
    # need to find min and max values for x-axis
    # assume base 2 log scale {2^min, 2^max}
    x1 = 0
    x2 = 5
    # need to find min and max values for y-axis
    y1 = 0
    y2 = 5
    series_keys = sorted(graph_map.keys())
    num_series = len(series_keys)
    for index in range(len(series_keys)):
        key = series_keys[index]
        series = graph_map[key]
        #print "The series is ", series
        # we can just plot the series directly, but just in case we add support
        # for error bars etc and use {x,y,stddev,etc...} in future, we will pull out 
        # the values for plotting manually.
        values = [[v[0],v[1]] for v in series]
        #print "the values are ", values
        axes.loglog(*zip(*values), basex=2, basey=2, markersize=8, marker=marker.next(), color=colors.next())
        # track max x value for scaling of axes nicely
        xvalues = sorted([x[0] for x in values])
        # we want a nice factor of 2 for our axes limits
        x2 = maximum({x2,int(math.log(maximum(xvalues,8),2))},x2)
    #print "Min and Max for X-axes are %f %f " % (x1, x2)
    # generate x labels for each power of 2
    xlabels = tuple(i for i in (2**x for x in range(x1,x2+1)) )
    # setup the xaxis parameters
    axes.set_xscale('log', basex=2)
    axes.set_xlim(minimum(xlabels,1), maximum(xlabels,3)*1.5)
    axes.set_xticklabels(xlabels)
    axes.set_xlabel(labelstrings[0])
    # ylabels should also be automatic, but for now, do them by hand
    # these should be GB/s or MB/s etc etc
    ylabels = [0.25, 0.5,1,2,4,8,16]
    # setup the yaxis parameters
    axes.set_yscale('log', basey=2)
    axes.set_ylim(0.25, 16 )
    axes.set_yticklabels(ylabels)
    axes.set_ylabel(labelstrings[1])
    axes.tick_params(axis='x', which='major', labelsize=9)
    #
    # define some custom minor tick locations on y axis:
    #
    #axes.yaxis.set_minor_formatter(plt.FormatStrFormatter('%8.4d'))
    axes.yaxis.set_minor_locator(plt.FixedLocator([0.375,0.75,1.5,3,6,12]))
    axes.tick_params(axis='y', which='minor', labelsize=8)
    axes.grid(b=True, which='major', color='b', linestyle='-')
    axes.grid(b=True, which='minor', color='g', linestyle='--')
    # coordinates are window coordinates from 0 to 1 
    axes.set_title(labelstrings[2], fontsize=10)
    
#----------------------------------------------------------------------------
def plot_configuration(graph_map, names) :

    fig = plt.figure(figsize = options.fig_size[0])
    axes = []
    
    # the supplied graphs come as a 2D array of params
    num_param1 = len(graph_map.keys())
    num_param2 = len(graph_map[graph_map.keys()[0]].keys())
    numrows = num_param1
    numcols = num_param2

    # if the arrays is 1xN or Nx1, rearrange the num rows/cols
    # to fit the page a little better instead of having one long line of plots
    if (num_param1==1) or (num_param2==1):
      total = num_param1*num_param2
      better = int(math.sqrt(total))
      numrows = better
      numcols = total/better     
      print "Rearranged graphs using layout %i x %i" % (numrows, numcols)
      
    # create an array of graphs for our parameter space
    # grid cells are defined by {row, col} from top left and down
    print "Creating array of graphs rows %i, cols %i" % (numrows, numcols)
    for r in range(numrows):
      for c in range(numcols):
        axes.append( plt.subplot2grid((numrows, numcols), (r, c), colspan=1) )
        
    # loop over input arrays/maps and create the actual plot data for each graph
    row = 0
    col = 0
    graph_keys = sorted(graph_map.keys())
    for param1_types in range(len(graph_keys)):
        param1_key     = graph_keys[param1_types]
        param1_results = graph_map[param1_key]
        param1_keys    = sorted(param1_results.keys())
        print "param1_ type ", param1_key
        for param2_size in range(len(param1_keys)):
            param2_key     = param1_keys[param2_size]
            param2_results = param1_results[param2_key]
            param2_keys    = sorted(param2_results.keys())
            print "param2_ type ", param2_key
            plot_one_collection(param2_results, ["Nodes", "BW/GB/s", names[2] + " " + sizeof_fmt(param2_key)], axes[col + row*numcols])
            col += 1
            if (col>=numcols):
              col = 0
              row += 1
        
    # legendIndexWrite = 3
    # legendIndexRead  = 7


    # for line in range(3):
        # axes[legendIndexWrite].plot([1], label=names[line], markersize=8, marker=markers[line/2],color=colors[line])
    # for line in range(3,6):
        # axes[legendIndexRead].plot([1], label=names[line], markersize=8, marker=markers[(line)/2],color=colors[line])
        
    # axes[legendIndexWrite].axis('off')
    # axes[legendIndexWrite].legend(loc='center', ncol=1, shadow=True, bbox_to_anchor=[0.5, 0.5], title=options.title, fontsize=12)
    # l = axes[legendIndexWrite].legend(title=options.title) 
    # l.get_title().set_fontsize(15)
    # axes[legendIndexRead].axis('off')
    # axes[legendIndexRead].legend(loc='center', ncol=1, shadow=True, bbox_to_anchor=[0.5, 0.5], title=options.title, fontsize=12)
    # l = axes[legendIndexRead].legend(title=options.title) 
    # l.get_title().set_fontsize(15)

    plt.tight_layout()
    if options.show_graph :
        plt.show()
    return fig

if len(args) == 0 :
    print "No input CSV file given"
    exit(0)

#----------------------------------------------------------------------------
def insert_safe(a_map, key1, key2, key3, value) :
  if not (key1) in a_map:
    a_map[key1] = {}
  if not (key2) in a_map[key1]:
    a_map[key1][key2] = {}
  if not (key3) in a_map[key1][key2]:
    a_map[key1][key2][key3] = []    
  a_map[key1][key2][key3].append(value)
  
#----------------------------------------------------------------------------
#
# read results data in and generate arrays/maps of values
# for each parcelport, threadcount, blocksize, ...
for csvfile in args :
    with open(csvfile) as f:
      io = StringIO(f.read().replace(':', ','))
      reader = csv.reader(io)
      Read_Net_Blocksize_Thread  = {}
      Write_Net_Blocksize_Thread = {}
      rownum = 0
      for row in reader:
          readflag = row[1].strip() in ("read")
          Network  = row[3]
          Nodes    = int(row[5])
          Threads  = int(row[7])
          IOPsize  = int(row[11])
          IOPs     = float(row[13])
          BW       = float(row[15])
          if (BW==0.0) : 
            BW = 1.0
          #print "read=%i Network=%s Nodes=%4i Threads=%3i IOPsize=%9i IOPs=%6.1f BW=%6.1f"  % (readflag, Network, Nodes, Threads, IOPsize, IOPs, BW)
          
          if (readflag):
            #print "Adding Read data ", [Nodes,BW]
            insert_safe(Read_Net_Blocksize_Thread, Network, IOPsize, Threads, [Nodes,BW])
          else :
            #print "Adding Write data ", [Nodes,BW]
            insert_safe(Write_Net_Blocksize_Thread, Network, IOPsize, Threads, [Nodes,BW])
          rownum += 1
          
    # output file path for svg/png
    base = os.path.splitext(csvfile)[0]
    graphs_to_print = []

    # generate one graph per blocksize for each threadcount
    fig_Read1  = plot_configuration(Read_Net_Blocksize_Thread, ["Read", Network, "Block size", "Threads"])
    graphs_to_print.append([fig_Read1,"Read1"])

    # generate graph using one set of data
#    fig_Write1 = plot_configuration(Write_Net_Blocksize_Thread, ["Write", Network, "Block size", "Threads"])
#    graphs_to_print.append([fig_Write1,"Write1"])
    
    for fig in graphs_to_print:
      svg_name = base + "." + fig[1] + ".svg"
      png_name = base + "." + fig[1] + ".png"
      print "Writing %s and %s" % (svg_name, png_name)
      fig[0].savefig(svg_name)
      fig[0].savefig(png_name)
    