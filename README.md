## About this repository

The purpose of this repository is to
help collaborators in the neutron data standards
project to keep track of the changes introduced
to the GMA database file and to explore the impact
of modifications and additions.

This repository makes use of the Python packages [poetry]
and [Data Version Control][dvc]
for a transparent database update process that can be reproduced
by anyone (who uses, for the time being, Linux or MacOS).

### Structure of this repository

This repository contains database files in the GMA format
and equivalent JSON files. There are two base files available in
this repository:

- `database/data2017.json` and `database/data2017.gma` contain
   the neutron standards database as used in the
   [std2017 evaluation][std2017-paper].
- `database/data.json` and `database/data.gma` are based on
   `data2017.json` and updated with
   data from the NIFFTE collaboration, see [Neudecker2021], and
   also a more elaborate uncertainty quantification using templates
   by [Neudecker2020].

The `codes/` subdirectory includes the codes to introduce
modifications to the database and to perform evaluations.
They will not be covered here because they do not need to be called
directly by the user. They are called indirectly via [dvc] commands,
see the next section.

The `codes/gmapy/` folder is a git submodule with the Python evaluation
code [gmapy]---an improved yet backward-compatible version of [GMAP].
This code is invoked to perform the statistical analysis based on
the experiments in the automatically produced `database/testdata.json` file.

`codes/database_modifications/` contains small Python scripts to modify
the database in different ways, e.g., remove specific types of experimental
data. Each script must possess an `apply` function that takes a
datablock list (e.g., see
[here](https://raw.githubusercontent.com/IAEA-NDS/neutron-standards-database/main/database/data2017.json)
and search for `datablocks` to see a datablock list) and return a datablock
list.

The file `params.yaml` contains the parameters to control the evaluation process
and will be explained in more detail at some point in the future.
As an example, the `ops` array contains the sequence of scripts in
`codes/database_modifications/` that should be applied to the base database
specified in the field `dbname`.

The `results/` directory contains csv files with the results of the
cross sections relative to the standards 2017 values.
The `MT` number in the file name designates the reaction type,
see [here](https://github.com/IAEA-NDS/gmapy/blob/master/DOCUMENTATION.md)
for available types.
The values behind `R1`, `R2`, etc. are identification numbers indicating
the involved reactions. Inspect the `database/data.json` file to find the
association between the `ID` number with the reaction given in `CLAB`.

The `eval2017/` directory contains the same file types as `results/`
but with the results for the standards 2017 evaluation.


### Installation of the pipeline

#### Required software on your system

In order to easily reproduce evaluation studies shared via this repository,
you need the Python package [poetry]. It can be installed by
```
pip install poetry
```
This package is a Python package manager. It helps in the management
of virtual environments to avoid cluttering your system and ensures
that the correct versions are installed in such virtual environments.

You also need the [SuiteSparse] library to be available on your system.
On Linux distributions using `apt`, it can be installed via
```
sudo apt-get install libsuitesparse-dev
```
If you are on MacOS, you can install it via
```
brew install suite-sparse
```
Before you proceed, it is a good idea to close and reopen the terminal
window to ensure that the `PATH` variable is appropriately updated.

#### Setting up the pipeline

First, clone this repository via
```
git clone --recurse-submodules https://github.com/iaea-nds/neutron-standards-database.git
```
Next, change into the created `neutron-standards-database` directory and run
```
poetry install
```
It will create a virtual environment and download all the dependencies including [dvc]
to run the pipeline.
If this command fails with a complaint about `cholmod.h` not being available,
it means that the compiler cannot find the SuiteSparse headers and libraries.
In this case, you need to define their location manually. Here are the necessary
instructions with typical installation paths:
```
export SUITESPARSE_INCLUDE_DIR=/opt/local/include
export SUITESPARSE_LIBRARY_DIR=/opt/local/lib
```
Afterwards, re-run `poetry install`.


### Reproducing evaluation studies

The explanation of the full functionality of [dvc] to manage
computational experiments is beyond the scope of this section.
Some examples of usage are given nevertheless to get interested
people started.

From within the `neutron-standards-database` directory, first run
```
poetry shell
```
This command will activate the virtual environment (created via `poetry install` above).

Now you can use the functionality of `git` in combination with `dvc`
to explore, modify and reproduce evaluation studies.
For instance, list available experiments per `git branch -a`.
Check out one of the branches, e.g.,
```
git checkout c2.new-input
```
To re-produce the results in `results/`, you can run
```
dvc exp run -n test_exp
```
As the files are already there, the stages in the pipeline will be skipped.
If you change now some value in the `params.yaml` file, e.g., `maxiter`,
and execute again the command above, the evaluation based on the updated
parameters will be performed.

There are many more useful commands, such as
```
dvc exp show -A
```
that shows the performed computational studies and which parameters have been
used.

You can also create plots comparing the results using different parameters.
For instance, make some branches locally available,
```
git checkout c1.std2017-new-code
git checkout c2.new-input
```
and afterwards run
```
dvc plots diff c1.std2017-new-code c2.new-input
```
It will generate by default a file `dvc_plots/index.html`
that you can open in your browser to see all plots at once.

### Troubleshooting

Issues that users may encounter are collected here.

- *dvc exp run* yieles the error message
*ERROR: unexpected - 'cannot stash changes - there is nothing to stash.'*
This can be solved by making a change in a file under git version control
that does not impact the result of the pipeline execution. For instance,
adding a blank line at the end of *params.yaml* solves the issue.


[dvc]: https://dvc.org/
[poetry]: https://python-poetry.org/
[std2017-paper]: https://www.sciencedirect.com/science/article/pii/S0090375218300218
[Neudecker2021]: https://www.osti.gov/biblio/1788383
[Neudecker2020]: https://www.sciencedirect.com/science/article/abs/pii/S0090375219300729
[GMAP]: https://github.com/IAEA-NDS/GMAP-Fortran
[gmapy]: https://github.com/iaea-nds/gmapy
[SuiteSparse]: https://github.com/DrTimothyAldenDavis/SuiteSparse
