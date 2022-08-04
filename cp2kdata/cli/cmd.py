from email.policy import default
import click
from .funcs import *


@click.group("cli")
def cli():
    pass

@click.group("gen")
def gen():
    click.echo('Generating CP2K Testing Inputs')

cli.add_command(gen)

@click.command()
@click.option(
    '--target_dir', 
    type=str, 
    default=".", 
    help='test directories are generated under target directory'
    )
@click.option(
    '--cutoff_range', 
    '-crange', 
    type=(int, int, int), 
    default=(300, 601, 50), 
    help='cutoff range, min, max, stepsize'
    )
@click.option(
    '--scf_converge', 
    type=bool, 
    default=False,
    help="whether converge scf"
    )
@click.argument('cp2k_input_file', type=str, nargs=1)
@click.argument(
    'other_file_list', 
    type=str, 
    nargs=-1,
    default=None
    )
def cutoff(cp2k_input_file, target_dir, cutoff_range, other_file_list, scf_converge):
    inp = get_CP2K(cp2k_input_file)
    #click.echo(other_file_list)
    write_cutoff_test_inp(
        inp, 
        target_dir=target_dir, 
        cutoff_range=cutoff_range,
        other_file_list=other_file_list,
        scf_converge=scf_converge)


gen.add_command(cutoff)
