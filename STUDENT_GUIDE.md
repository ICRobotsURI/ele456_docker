# Foundations for Robotics - Environment Setup Guide

This guide will help you set up the course development environment on your computer. By the end, you will have a fully working ROS 2 + Gazebo desktop accessible from your web browser.

**Time required:** ~30 minutes (mostly waiting for downloads)

---

## What You Are Setting Up

You will run a virtual Linux desktop inside Docker (a lightweight container system). This desktop has everything pre-installed:

- Ubuntu 24.04
- ROS 2 Jazzy (the robotics framework)
- Gazebo Harmonic (the 3D robot simulator)
- All tools needed for the course (rviz2, rqt, colcon, etc.)

You access this desktop through your web browser. No Linux installation required on your machine.

---

## Step 1: Install Docker Desktop

Download and install Docker Desktop for your operating system:

### Windows

1. Go to https://www.docker.com/products/docker-desktop/
2. Click **Download for Windows**
3. Run the installer (Docker Desktop Installer.exe)
4. Follow the installation wizard. Accept all defaults.
5. When prompted, **enable WSL 2** (this is the recommended option)
6. Restart your computer when asked
7. After restart, Docker Desktop will start automatically. Wait until it says **"Docker Desktop is running"** in the system tray (bottom-right of your screen, the whale icon)

**If you see "WSL 2 installation is incomplete":**
- Open PowerShell as Administrator
- Run: `wsl --install`
- Restart your computer again

### macOS

1. Go to https://www.docker.com/products/docker-desktop/
2. Click **Download for Mac**
   - If you have a Mac with Apple Silicon (M1, M2, M3, M4): choose **Apple Silicon**
   - If you have an older Intel Mac: choose **Intel Chip**
   - Not sure? Click the Apple logo (top-left) → "About This Mac" → look for "Chip"
3. Open the downloaded .dmg file
4. Drag Docker to Applications
5. Open Docker from Applications
6. Accept the terms and wait until it says **"Docker Desktop is running"** in the menu bar (top-right, whale icon)

### Linux (Ubuntu/Debian)

Open a terminal and run these commands one at a time:

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo usermod -aG docker $USER
```

**Important:** Log out and log back in after the last command (or restart your computer). This allows you to use Docker without `sudo`.

---

## Step 2: Start Docker Desktop and Sign In

After installation, you need to open Docker Desktop for the first time and create an account.

1. Open **Docker Desktop** from your Applications (Mac) or Start Menu (Windows)
2. You will be asked to sign in or create an account. Click **Sign Up** if you don't have one, or **Sign in with Google** using your student email.
3. Accept the terms of service if prompted
4. Wait until Docker Desktop shows it is **running** (whale icon in system tray on Windows, or menu bar on Mac, stops animating)

**You must do this every time you restart your computer before running any docker commands.** If Docker Desktop is not running, docker commands will fail.

---

## Step 3: Download the Course Files

Your instructor will provide a folder (or .zip file) containing these files:

```
ros2-environment/
├── Dockerfile
├── docker-compose.yml
├── start.sh
├── supervisord.conf
└── STUDENT_GUIDE.md  (this file)
```

Place this folder somewhere convenient. For example:
- Windows: `C:\Users\YourName\Documents\ros2-environment`
- Mac: `~/Documents/ros2-environment`
- Linux: `~/ros2-environment`

---

## Step 4: Build and Start the Environment

### Open a terminal in the course folder

**Windows:**
- Open the folder in File Explorer
- Click in the address bar at the top, type `cmd`, and press Enter
- A command prompt will open in that folder

**macOS:**
- Open Terminal (Applications → Utilities → Terminal)
- Type `cd ` (with a space after cd), then drag the folder from Finder into the terminal window, and press Enter

**Linux:**
- Open a terminal
- Run: `cd ~/ros2-environment` (or wherever you placed the folder)

### Build the environment (first time only)

Run this command:

```
docker compose up --build
```

**This will take 15-25 minutes** the first time. It downloads and installs Ubuntu, ROS 2, Gazebo, and all tools. You will see a lot of text scrolling by. This is normal.

Wait until you see output that looks like:

```
ros2-classroom  | 2024-XX-XX XX:XX:XX,XXX INFO success: tigervnc entered RUNNING state
ros2-classroom  | 2024-XX-XX XX:XX:XX,XXX INFO success: novnc entered RUNNING state
```

This means the environment is ready.

### Next time (starting without rebuilding)

After the first build, you only need:

```
docker compose up
```

This starts in seconds.

---

## Step 5: Access Your Desktop

1. Open your web browser (Chrome, Firefox, Edge, Safari — any modern browser)
2. Go to: **http://localhost:6080**
3. You will see a noVNC connection page. Click **Connect**
4. Enter the password: **student**
5. You now have a full Linux desktop in your browser!

---

## Step 6: Verify Everything Works

Once inside the desktop:

1. **Open a terminal:** Right-click on the desktop → "Open Terminal Here" (or find "Terminal" in the bottom taskbar)

2. **Check ROS 2 is working:**
   ```bash
   ros2 --help
   ```
   You should see a list of ROS 2 commands.

3. **Check Gazebo is working:**
   ```bash
   gz sim --versions
   ```
   You should see version information for Gazebo Harmonic.

4. **Run a quick test (optional):**
   ```bash
   ros2 launch turtlebot4_gz_bringup turtlebot4_gz.launch.py
   ```
   You should see Gazebo open with a TurtleBot 4 robot in a default world. This may take a moment to load the first time.

   Press `Ctrl+C` to stop it.

---

## Daily Usage

### Starting your session

```
docker compose up
```

Then open http://localhost:6080 in your browser.

### Stopping your session

In the terminal where you ran `docker compose up`, press `Ctrl+C`.

Or, in a separate terminal in the same folder:

```
docker compose down
```

### Your work is saved automatically

The `ros2_ws` folder (your ROS workspace) persists between sessions. You will not lose your code when you stop the container.

---

## Working with ROS 2 (Quick Reference)

All commands below are run inside the desktop terminal (in the browser).

### Your workspace

Your ROS 2 workspace is at: `~/ros2_ws`

This is where you will create and build your packages.

### Creating a new package

```bash
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_python my_package
```

### Building your workspace

```bash
cd ~/ros2_ws
colcon build
source install/setup.bash
```

### Running a node

```bash
ros2 run my_package my_node
```

### Launching the TurtleBot4 simulation

```bash
ros2 launch turtlebot4_gz_bringup turtlebot4_gz.launch.py
```

To launch the Lite version:

```bash
ros2 launch turtlebot4_gz_bringup turtlebot4_gz.launch.py model:=lite
```

### Controlling the robot with keyboard

In a second terminal:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

---

## Troubleshooting

### "Cannot connect to the Docker daemon"

Docker Desktop is not running. Open Docker Desktop and wait for it to fully start (whale icon stops animating).

### "port is already allocated" error

Something else is using port 6080. Stop the other program, or change the port in docker-compose.yml:

Change `"6080:6080"` to `"7080:6080"`, then access via http://localhost:7080

### The build fails with a network error

Your internet connection may have dropped during the build. Run:

```
docker compose up --build
```

again. Docker will resume from where it left off.

### The desktop is slow or laggy

- Close other browser tabs to free memory
- Make sure Docker Desktop has at least 4 GB of RAM allocated:
  - Windows/Mac: Docker Desktop → Settings → Resources → Memory → set to 4 GB or more
- If still slow, reduce resolution by stopping the container, editing `docker-compose.yml`, changing `VNC_RESOLUTION=1920x1080` to `VNC_RESOLUTION=1280x720`, then starting again

### Gazebo shows a black screen or crashes

Gazebo uses GPU rendering. Inside Docker, this runs in software mode which is slower but functional. If Gazebo crashes:

- Increase Docker's memory allocation to 6+ GB
- Try running Gazebo headless for testing: `gz sim -s empty.sdf` (server only, no GUI)

### "I accidentally deleted my container"

Your code in `ros2_ws` is safe — it lives in a Docker volume. Just run `docker compose up` again and your workspace will still be there.

### "I want to start completely fresh"

If something is badly broken and you want to reset everything:

```
docker compose down -v
docker compose up --build
```

**Warning:** The `-v` flag removes your workspace volume. You will lose any code inside `ros2_ws`. Back up your code first!

### I cannot copy/paste between my computer and the desktop

noVNC has a clipboard panel. Look for a small arrow tab on the left edge of the browser window. Click it, and you will see a text area. Paste text there, and it becomes available inside the desktop (Ctrl+V). To copy from inside to outside, select text inside, it appears in that panel, then copy from there.

---

## System Information

| Component | Version |
|-----------|---------|
| Ubuntu | 24.04 LTS (Noble Numbat) |
| ROS 2 | Jazzy Jalisco (LTS) |
| Gazebo | Harmonic (LTS) |
| Python | 3.12 |

### Pre-installed ROS 2 packages

- `ros-jazzy-desktop` (core + rviz2 + rqt + demos)
- `ros-jazzy-ros-gz` (Gazebo integration)
- `ros-jazzy-turtlebot4-simulator` (TurtleBot4 Gazebo simulation)
- `ros-jazzy-irobot-create-nodes` (iRobot Create3 base nodes)
- `ros-jazzy-turtlebot4-desktop` (visualization and tools)
- `ros-jazzy-navigation2` (Nav2 autonomous navigation stack)
- `ros-jazzy-xacro` (robot description macros)
- `ros-jazzy-teleop-twist-keyboard` (keyboard teleoperation)
- `ros-jazzy-joint-state-publisher-gui` (joint control GUI)
- `ros-jazzy-robot-state-publisher` (TF publisher from URDF)
- `ros-dev-tools` (colcon, rosdep, vcstool, etc.)
- `gz-harmonic` (Gazebo Harmonic full installation)
- Visual Studio Code
- gedit

### Login credentials

- **Username:** student
- **Password:** student
- This user has full sudo access (no password required for sudo).

---

## Getting Help

If you have issues not covered here:

1. Check that Docker Desktop is running and healthy
2. Try stopping and restarting: `docker compose down` then `docker compose up`
3. Check Docker logs: `docker compose logs`
4. Ask your instructor or TA
