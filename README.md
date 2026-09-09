# ELE 456 — Foundations of Robotics

Development environment and course materials for ELE 456. The environment runs Ubuntu 24.04, ROS 2 Jazzy, and Gazebo Harmonic inside Docker, with a Linux desktop accessible through your web browser.

## Getting started

1. Download this repository using **Code → Download ZIP**, then extract the ZIP. If you use Git, you can clone it instead:
   ```bash
   git clone https://github.com/ICRobotsURI/ele456_docker.git
   ```
2. Follow the **[Student Setup Guide](STUDENT_GUIDE.md)** to install Docker and prepare your computer.
3. Start Docker Desktop (on Windows or macOS), then open a terminal in the downloaded folder containing `docker-compose.yml`.
4. Build and start the environment:
   ```bash
   docker compose up --build
   ```
   The first build downloads and installs the required software and may take a while.
5. Open **http://localhost:6080** in your browser, click **Connect**, and enter the password **`student`**.

## Daily use

Run this command from the downloaded repository folder to start the environment after the initial build:

```bash
 docker compose up
```

Open http://localhost:6080 to access your Linux desktop. To stop the environment, press **Ctrl+C** in the terminal running Docker Compose, or run `docker compose down` from another terminal in the repository folder.

Your ROS workspace is stored in a persistent Docker volume. Stopping the container preserves your work. **Do not run `docker compose down -v` unless you intend to delete the workspace and have backed up your files.**

## Working inside the Linux desktop

Open a terminal inside the browser desktop. Your ROS workspace is located at `~/ros2_ws`, and the course packages are in `~/ros2_ws/src`.

To launch the course simulation with RViz visualization:

```bash
ros2 launch course_project sim_headless.launch.py
```

To use the second cylinder world:

```bash
ros2 launch course_project sim_headless.launch.py world:=world_2
```

After editing your ROS package, rebuild and source the workspace:

```bash
cd ~/ros2_ws
colcon build
source install/setup.bash
```

The container workspace is a Docker volume, not a live copy of the downloaded repository folder. Edit your course code in `~/ros2_ws/src` inside the Linux desktop and back up your work separately.

## Course materials

- [Student Setup Guide](STUDENT_GUIDE.md): installation, daily usage, and troubleshooting.
- [Final Project Assignment](ELE456_Final_Project.docx): project requirements, evaluation, and submission instructions.
- [Course simulation package](packages/course_project): robot model, worlds, launch files, and RViz configuration.
- [Student Python package](packages/my_package): ROS node examples, mapping example, and practice graders.

For setup problems, start with the troubleshooting section of the [Student Setup Guide](STUDENT_GUIDE.md).
