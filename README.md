# Overview

Use the following command to initialise the submodules:

```bash
git submodule update --init --recursive
```

Build the docker file:

```bash
docker build -t bisimulation .
```

Run the docker container, and bind the output directory:

```bash
docker run -it --mount type=bind,source=./output/,target=/root/output bisimulation
```

Within the container, run the following command to prepare the input for the
bisimulation checking:

```bash
python3 /root/scripts/prepare.py --mcrl2-path /root/mCRL2/build/stage/bin/ --input-dir /root/cases/ --output-dir /root/input
```