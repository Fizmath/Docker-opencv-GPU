ARG CUDA_VERSION=10.2
ARG CUDNN_VERSION=7
ARG UBUNTU_VERSION=18.04

FROM nvidia/cuda:${CUDA_VERSION}-cudnn${CUDNN_VERSION}-devel-ubuntu${UBUNTU_VERSION}
LABEL mantainer="  github.com/Fizmath   < boy.cosmic@yandex.by >    "

ARG PYTHON_VERSION=3.8
ARG OPENCV_VERSION=4.5.0

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get -qq update && \
    apt-get -qq install  \
#   python :
        python${PYTHON_VERSION} \
        python${PYTHON_VERSION}-dev \
        libpython${PYTHON_VERSION} \
        libpython${PYTHON_VERSION}-dev \
        python-dev \
        python3-setuptools \
#   developement tools, opencv image/video/GUI dependencies, optimiztion packages , etc ...  :
        apt-utils \
        autoconf \
        automake \
        checkinstall \
        cmake \
        gfortran \
        git \
        libatlas-base-dev \
        libavcodec-dev \
        libavformat-dev \
        libavresample-dev \
        libeigen3-dev \
        libexpat1-dev \
        libglew-dev \
        libgtk-3-dev \
        libjpeg-dev \
        libopenexr-dev \
        libpng-dev \
        libpostproc-dev \
        libpq-dev \
        libqt5opengl5-dev \
        libsm6 \
        libswscale-dev \
        libtbb2 \
        libtbb-dev \
        libtiff-dev \
        libtool \
        libv4l-dev \
        libwebp-dev \
        libxext6 \
        libxrender1 \
        libxvidcore-dev \
        pkg-config \
        protobuf-compiler \
        qt5-default \
        unzip \
        wget \
        yasm \
        zlib1g-dev \
#   GStreamer :
        libgstreamer1.0-0 \
        gstreamer1.0-plugins-base \
        gstreamer1.0-plugins-good \
        gstreamer1.0-plugins-bad \
        gstreamer1.0-plugins-ugly \
        gstreamer1.0-libav \
        gstreamer1.0-doc \
        gstreamer1.0-tools \
        gstreamer1.0-x \
        gstreamer1.0-alsa \
        gstreamer1.0-gl \
        gstreamer1.0-gtk3 \
        gstreamer1.0-qt5 \
        gstreamer1.0-pulseaudio \
        libgstreamer1.0-dev \
        libgstreamer-plugins-base1.0-dev && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get purge   --auto-remove && \
    apt-get clean

# install new pyhton system wide :
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.6 1 && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python${PYTHON_VERSION} 2 && \
    update-alternatives --config python3

# numpy for the newly installed python :
RUN wget https://bootstrap.pypa.io/get-pip.py  && \
    python${PYTHON_VERSION} get-pip.py --no-setuptools --no-wheel && \
    rm get-pip.py && \
    pip install numpy

# opencv and opencv-contrib :
RUN cd /opt/ &&\
    wget https://github.com/opencv/opencv/archive/${OPENCV_VERSION}.zip -O opencv.zip &&\
    unzip -qq opencv.zip &&\
    rm opencv.zip &&\
    wget https://github.com/opencv/opencv_contrib/archive/${OPENCV_VERSION}.zip -O opencv-co.zip &&\
    unzip -qq opencv-co.zip &&\
    rm opencv-co.zip &&\
    mkdir /opt/opencv-${OPENCV_VERSION}/build && cd /opt/opencv-${OPENCV_VERSION}/build &&\
    cmake \
      -D BUILD_opencv_java=OFF \
      -D WITH_CUDA=ON \
      -D WITH_CUBLAS=ON \
      -D OPENCV_DNN_CUDA=ON \
      -D CUDA_ARCH_PTX=7.5 \
      -D WITH_NVCUVID=ON \
      -D WITH_CUFFT=ON \
      -D WITH_OPENGL=ON \
      -D WITH_QT=ON \
      -D WITH_IPP=ON \
      -D WITH_TBB=ON \
      -D WITH_EIGEN=ON \
      -D CMAKE_BUILD_TYPE=RELEASE \
      -D OPENCV_EXTRA_MODULES_PATH=/opt/opencv_contrib-${OPENCV_VERSION}/modules \
      -D PYTHON2_EXECUTABLE=$(python${PYTHON_VERSION} -c "import sys; print(sys.prefix)") \
      -D CMAKE_INSTALL_PREFIX=$(python${PYTHON_VERSION} -c "import sys; print(sys.prefix)") \
      -D PYTHON_EXECUTABLE=$(which python${PYTHON_VERSION}) \
      -D PYTHON_INCLUDE_DIR=$(python${PYTHON_VERSION} -c "from distutils.sysconfig import get_python_inc; print(get_python_inc())") \
      -D PYTHON_PACKAGES_PATH=$(python${PYTHON_VERSION} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())") \
      -D CUDA_TOOLKIT_ROOT_DIR=/usr/local/cuda \
      -D CMAKE_LIBRARY_PATH=/usr/local/cuda/lib64/stubs \
        .. &&\
    make -j$(nproc) && \
    make install && \
    ldconfig &&\
    rm -rf /opt/opencv-${OPENCV_VERSION} && rm -rf /opt/opencv_contrib-${OPENCV_VERSION}

ENV NVIDIA_DRIVER_CAPABILITIES all
ENV XDG_RUNTIME_DIR "/tmp"

WORKDIR /myapp