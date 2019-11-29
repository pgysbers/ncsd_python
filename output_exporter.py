"""Module for helping to deal with data from NCSD output files,
and export that data to different formats."""

from plot_modules import scraper
from plot_modules import ncsd_output_reader
from plot_modules import plotter
from os.path import realpath, dirname, join, exists
from os import mkdir
import argparse

# path to grace_spectra_plotter
grace_plotter_path = realpath("grace_spectra_plotter.exe")

# if you're running this file on its own, edit the variables below!
# but make sure to leave the function as-is, so you can still run with "-f"

# output_paths = paths to ncsd output files
output_paths = ["/Users/callum/Desktop/rough_code/ncsd_python/example_files/Li8_n3lo-NN3Nlnl-srg2.0_Nmax0-10.20"]

# save_dir = where to save the plot files, formatted as "string" or None.
# None = save in the same directory as the first output_paths file
# blank string = current working directory
# some other string = save to that directory, include a final slash
save_dir = None

# output_type is the kind(s) of output you want, in a list
# possible output types: xmgrace, csv, matplotlib
# FYI, the output is saved in the same directory as this script.
out_types = ["xmgrace", "matplotlib", "csv"]

# if there are any Nmax values you want to skip, put them here,
# e.g. [0,2,4]. If you don't want to skip any, use []
skip_Nmax = []

# states and only want to plot 8, use this.
# if you don't want a max state, set max_state to a huge number, e.g. 1e100
max_state = 1e100

# get_online_data sets whether or not the program tries to get data from online
get_online_data = False

def make_plot_files(
   output_paths=[],
   save_dir=None,
   out_types=["xmgrace"],
   skip_Nmax=[],
   max_state=1e100,
   get_online_data=False):
    """
    This takes ncsd output filenames,
    and exports the data to each format listed in out_types.
    
    skip_Nmax = list of Nmax values to skip

    max_state = maximum numbered state to consider
    """
    if output_paths == []:
        raise ValueError("must specify at least one output path")
    if type(output_paths) != list:
        output_paths = [output_paths]
    
    if save_dir is None:  # set it to something logical, 
        save_dir = dirname(output_paths[0])

    # convert paths to full paths if they're relative
    output_paths = [realpath(path) for path in output_paths]
    save_dir = realpath(save_dir)

    # make sure the save directory exists
    if not exists(save_dir):
        try:
            mkdir(save_dir)
        except:
            raise IOError("Save directory " + save_dir + " does not exist!")

    # grab input from output of ncsd
    ncsd_data = ncsd_output_reader.read_all_ncsd_output(output_paths)
    # tries to get energy spectrum from online, but doesn't break if it fails
    experimental_data = scraper.get_online_data_wrapper(ncsd_data, get_online_data)
    
    # combine ncsd_data and experimental_data
    data = ncsd_data
    data["expt_spectrum"] = experimental_data["expt_spectrum"]
    data["skip_Nmax"] = skip_Nmax
    data["max_state"] = max_state

    # do something with the data, whether that's plotting or just making files
    for out_type in out_types:
        print("exporting as type "+out_type)
        plotter.export_data(
            data, save_dir, grace_plotter_path, out_type=out_type)


if __name__ == "__main__":
    # add argument parser so we can call this with
    # python output_exporter.py -f "filename"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-f','--file', help='Filename', required=False, default=[])
    args = parser.parse_args()
    if args.file != []:  # if filename provided
        make_plot_files(output_paths=args.file)
    else:
        make_plot_files(
            output_paths=output_paths,
            save_dir=save_dir,
            out_types=out_types,
            skip_Nmax=skip_Nmax,
            max_state=max_state,
            get_online_data=get_online_data)