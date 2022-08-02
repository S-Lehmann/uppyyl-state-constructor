# Uppyyl State Constructor

A Python implementation of a state constructor for Uppaal models.
The state constructor provides routines for determining sequences of DBM operations that construct given clock states, and routines for adapting a given model so that a particular state (consisting of clock state, variable state, and location state) is initialized during model execution.

## Getting Started

In this section, you will find instructions to setup the Uppyyl State Constructor on your local machine.

### Prerequisites

#### Python

Install Python >=3.8 for this project.

#### Virtual Environment

If you want to install the project in a dedicated virtual environment, first install virtualenv:
```
python3.8 -m pip install virtualenv
```

And create a virtual environment:

```
cd project_folder
virtualenv uppyyl-env
```

Then, activate the virtual environment on macOS and Linux via:

```
source ./uppyyl-env/bin/activate
```

or on Windows via:

```
source .\uppyyl-env\Scripts\activate
```

### Installing

To install the Uppyyl State Constructor directly from GitHub, run the following command:

```
python3.8 -m pip install -e git+https://github.com/S-Lehmann/uppyyl-state-constructor.git#egg=uppyyl-state-constructor
```

To install the project from a local directory instead, run:

```
python3.8 -m pip install -e path_to_project_root
```

## Authors

* **Sascha Lehmann** - *Initial work* - [S-Lehmann](https://github.com/S-Lehmann)

See also the list of [contributors](https://github.com/S-Lehmann/uppyyl-state-constructor/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

* The Uppaal model checking tool can be found at http://www.uppaal.org/.
* The project is associated with the [Institute for Software Systems](https://www.tuhh.de/sts) at Hamburg University of Technology.
