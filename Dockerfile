FROM ghcr.io/kivy/buildozer:latest
# See https://github.com/kivy/buildozer/blob/master/Dockerfile

# Buildozer will be installed in entrypoint.py
# This is needed to install version specified by user
RUN pip3 uninstall -y buildozer

# Get the latest JDK version as Buildozer requires the latest version to build the APK
RUN sudo apt-get update && \
    sudo apt-get install -y software-properties-common && \
    sudo rm -rf /var/lib/apt/lists/*
RUN sudo add-apt-repository ppa:openjdk-r/ppa
RUN sudo apt update
RUN sudo apt-get -y install openjdk-17-jdk

# Remove a lot of warnings
# sudo: setrlimit(RLIMIT_CORE): Operation not permitted
# See https://github.com/sudo-project/sudo/issues/42
RUN echo "Set disable_coredump false" | sudo tee -a /etc/sudo.conf > /dev/null

# By default Python buffers output and you see prints after execution
# Set env variable to disable this behavior
ENV PYTHONUNBUFFERED=1

# Set up venv and env
# Set venv vars
RUN python3 -m venv $HOME_DIR/.venv
ENV VIRTUAL_ENV=$HOME_DIR/.venv
ENV PATH=$HOME_DIR/.venv/bin:$PATH
# Buildozer settings to disable interactions
ENV BUILDOZER_WARN_ON_ROOT="0"
ENV APP_ANDROID_ACCEPT_SDK_LICENSE="1"
# Do not allow to change directories
ENV BUILDOZER_BUILD_DIR="./.buildozer"
ENV BUILDOZER_BIN="./bin"

# Install dependencies in venv
RUN python -m pip install setuptools

# Set up entrypoint
COPY entrypoint.py /action/entrypoint.py
ENTRYPOINT ["/action/entrypoint.py"]
