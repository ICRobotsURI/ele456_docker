# =============================================================================
# ROS 2 Jazzy + Gazebo Harmonic + XFCE Desktop + noVNC
# Foundations for Robotics - Course Environment
# =============================================================================
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8
ENV TZ=UTC

# ---- Basic system utilities and locale ----
RUN apt-get update && apt-get install -y \
    locales \
    curl \
    wget \
    gnupg2 \
    lsb-release \
    software-properties-common \
    sudo \
    git \
    nano \
    vim \
    htop \
    net-tools \
    iputils-ping \
    python3-pip \
    python3-venv \
    dbus-x11 \
    apt-transport-https \
    && locale-gen en_US.UTF-8 \
    && rm -rf /var/lib/apt/lists/*

# ---- XFCE Desktop Environment ----
RUN apt-get update && apt-get install -y \
    xfce4 \
    xfce4-goodies \
    xfce4-terminal \
    mousepad \
    thunar \
    && rm -rf /var/lib/apt/lists/*

# ---- gedit text editor ----
RUN apt-get update && apt-get install -y \
    gedit \
    && rm -rf /var/lib/apt/lists/*

# ---- Visual Studio Code ----
RUN wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /tmp/packages.microsoft.gpg && \
    install -D -o root -g root -m 644 /tmp/packages.microsoft.gpg /etc/apt/keyrings/packages.microsoft.gpg && \
    echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/keyrings/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list && \
    rm /tmp/packages.microsoft.gpg && \
    apt-get update && apt-get install -y code && \
    rm -rf /var/lib/apt/lists/*

# ---- TigerVNC + noVNC ----
RUN apt-get update && apt-get install -y \
    tigervnc-standalone-server \
    tigervnc-common \
    novnc \
    websockify \
    && rm -rf /var/lib/apt/lists/*

# ---- Supervisor (manages all processes) ----
RUN apt-get update && apt-get install -y \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# ---- ROS 2 Jazzy ----
RUN curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key | \
    gpg --dearmor -o /usr/share/keyrings/ros-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] \
    http://packages.ros.org/ros2/ubuntu $(lsb_release -cs) main" \
    > /etc/apt/sources.list.d/ros2.list && \
    apt-get update && apt-get install -y \
    ros-jazzy-desktop \
    ros-jazzy-ros-gz \
    ros-jazzy-xacro \
    ros-jazzy-joint-state-publisher \
    ros-jazzy-joint-state-publisher-gui \
    ros-jazzy-robot-state-publisher \
    ros-jazzy-teleop-twist-keyboard \
    ros-jazzy-rviz2 \
    ros-jazzy-rqt* \
    ros-jazzy-navigation2 \
    ros-jazzy-nav2-bringup \
    ros-dev-tools \
    python3-colcon-common-extensions \
    python3-rosdep \
    && rm -rf /var/lib/apt/lists/*

# ---- Gazebo Harmonic (standalone, for gz sim command) ----
RUN curl -sSL https://packages.osrfoundation.org/gazebo.gpg -o /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" > /etc/apt/sources.list.d/gazebo-stable.list && \
    apt-get update && apt-get install -y gz-harmonic && \
    rm -rf /var/lib/apt/lists/*

# ---- Initialize rosdep ----
RUN rosdep init && rosdep update

# ---- Create a non-root user (student) ----
RUN useradd -m -s /bin/bash -G sudo student && \
    echo "student:student" | chpasswd && \
    echo "student ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# ---- TurtleBot4 Simulator (official apt packages) ----
RUN apt-get update && apt-get install -y \
    ros-jazzy-turtlebot4-simulator \
    ros-jazzy-irobot-create-nodes \
    ros-jazzy-turtlebot4-desktop \
    && rm -rf /var/lib/apt/lists/*

# ---- Python packages for course (OpenCV, numpy) ----
RUN apt-get update && apt-get install -y \
    python3-opencv \
    python3-numpy \
    && rm -rf /var/lib/apt/lists/*

# ---- Course packages (pre-built) ----
COPY packages/course_project /home/student/ros2_ws/src/course_project
COPY packages/my_package /home/student/ros2_ws/src/my_package
RUN /bin/bash -c "source /opt/ros/jazzy/setup.bash && \
    cd /home/student/ros2_ws && \
    colcon build --symlink-install"

# ---- Setup ROS environment for the student user ----
RUN echo "source /opt/ros/jazzy/setup.bash" >> /home/student/.bashrc && \
    echo "source ~/ros2_ws/install/setup.bash 2>/dev/null" >> /home/student/.bashrc && \
    echo "export ROS_DOMAIN_ID=0" >> /home/student/.bashrc && \
    mkdir -p /home/student/ros2_ws/src && \
    chown -R student:student /home/student

# ---- VNC configuration ----
RUN mkdir -p /home/student/.vnc && \
    echo "student" | vncpasswd -f > /home/student/.vnc/passwd && \
    chmod 600 /home/student/.vnc/passwd && \
    chown -R student:student /home/student/.vnc

# ---- noVNC symlink for easy access ----
RUN ln -sf /usr/share/novnc/vnc.html /usr/share/novnc/index.html

# ---- Supervisor configuration ----
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# ---- Startup script ----
COPY start.sh /start.sh
RUN chmod +x /start.sh

# ---- Expose ports ----
# 6080: noVNC web interface
# 5901: VNC direct connection (optional)
EXPOSE 6080 5901

# ---- Set working directory ----
WORKDIR /home/student

# ---- Entrypoint ----
CMD ["/start.sh"]
