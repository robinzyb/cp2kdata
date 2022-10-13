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

@click.group("plot")
def plot():
    click.echo('Plot CP2K Testing Results')

cli.add_command(plot)

#-- for gen test --# 
#-- Cutoff --#
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
#-- Cutoff --#

#-- Basis --#
@click.command()
@click.option(
    '--target_dir', 
    type=str, 
    default=".", 
    help='test directories are generated under target directory'
    )
@click.option(
    '--test_element', 
    '-e', 
    type=str,
    default="O", 
    help='test element for basis set'
    )
@click.option(
    '--short_range',
    '-sr', 
    type=bool, 
    default=True,
    help="whether use short range basis set"
    )
@click.argument('cp2k_input_file', type=str, nargs=1)
@click.argument(
    'other_file_list', 
    type=str, 
    nargs=-1,
    default=None
    )
def basis(cp2k_input_file, target_dir, test_element, other_file_list, short_range):
    inp = get_CP2K(cp2k_input_file)
    #click.echo(other_file_list)
    write_basis_test_inp(
        inp, 
        target_dir=target_dir, 
        test_element=test_element,
        other_file_list=other_file_list,
        short_range=short_range)


gen.add_command(basis)
#-- Basis --#

#-- U --#
@click.command()
@click.option(
    '--target_dir', 
    type=str, 
    default=".", 
    help='test directories are generated under target directory'
    )
@click.option(
    '--u_range', 
    '-ur', 
    type=(float, float, float), 
    default=(0, 8, 1), 
    help='Hubbard U range: min, max, stepsize'
    )
@click.option(
    '--test_element', 
    '-e', 
    type=str,
    default="O", 
    help='test element for Hubbard U test'
    )
@click.option(
    '--test_orbital', 
    '-orb', 
    type=str,
    default="p", 
    help='test orbital for Hubbard U test'
    )
@click.argument('cp2k_input_file', type=str, nargs=1)
@click.argument(
    'other_file_list', 
    type=str, 
    nargs=-1,
    default=None
    )
def hubbardU(cp2k_input_file, target_dir, u_range, test_element, test_orbital, other_file_list):
    inp = get_CP2K(cp2k_input_file)
    #click.echo(other_file_list)
    write_hubbard_U_test_inp(
        inp, 
        target_dir=target_dir, 
        u_range=u_range,
        test_element=test_element,
        test_orbital=test_orbital,
        other_file_list=other_file_list)


gen.add_command(hubbardU)
#-- U --#

#-- for plot -- # 

#--cutoff --#
@click.command()
@click.option(
    '--target_dir', 
    type=str, 
    default=".", 
    help='plot ther results under target directory'
    )
def cutoff(target_dir):
    #click.echo(other_file_list)
    plot_cutoff_test(target_dir=target_dir)

plot.add_command(cutoff)

#--basis --#
@click.command()
@click.option(
    '--target_dir', 
    type=str, 
    default=".", 
    help='plot ther results under target directory'
    )
def basis(target_dir):
    #click.echo(other_file_list)
    plot_basis_test(target_dir=target_dir)
    
plot.add_command(basis)

#--U --#
@click.command()
@click.option(
    '--target_dir', 
    type=str, 
    default=".", 
    help='plot ther results under target directory'
    )
@click.option(
    '--exp_yaml', 
    type=str,
    default="No",
    help='experimental values'
    )
def hubbardU(target_dir, exp_yaml):
    #click.echo(other_file_list)
    if exp_yaml == "No":
        exp_collect=(None, None, None, None, None, None, None, None, None)
    else:
        exp_collect = get_exp_collect_from_yaml(exp_yaml)
    plot_U_test(target_dir=target_dir, exp_collect=exp_collect)

plot.add_command(hubbardU)

@click.command()
@click.option(
    '--fig_name',
    '-fn',
    type=str, 
    default="pKa.pdf", 
    help='name of fep figure'
    )
def ti(fig_name):
    plot_ti(fig_name=fig_name)

plot.add_command(ti)