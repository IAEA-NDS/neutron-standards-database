### About this repository

The purpose of this repository is to
help collaborators in the neutron data standards
project to keep track of the changes introduced
to the GMA database file.

The GMA database file is read by the GMAP code.
The original [Fortran-77 version][fortrangmap] has been translated
to a [Python version][pythongmap] that underwent significant
refactoring. The GMAP code implements the Generalized Least Squares method (GLS)
method, e.g., described on [Wikipedia][wikigls].
The mathematical specificities of the code regarding nuclear data evaluation
are available in a [report][poenitz81] published by Poenitz in 1981.

The format of the database file is explained to some extent in
[this report][gmaformat] and a brief [cheatsheet][gmacheat] is also available.

[poenitz81]: https://nds.iaea.org/standards/Reports/extract-from-indc-usa-85.pdf
[poenitz97]: https://nds.iaea.org/standards/Reports/ANL-NDM-139.pdf
[wikigls]: https://en.wikipedia.org/wiki/Generalized_least_squares 
[fortrangmap]: https://github.com/iaea-nds/gmap-fortran
[pythongmap]: https://github.com/IAEA-NDS/GMAP-Python
[gmaformat]: https://nds.iaea.org/standards/Reports/ANL-NDM-139.pdf
[gmacheat]: https://github.com/IAEA-NDS/GMAP-Python/blob/master/DOCUMENTATION.md 
