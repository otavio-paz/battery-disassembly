# Battery disassembly camera demo

This first MuJoCo milestone is deliberately stationary. It contains one SO-101 follower arm with its gripper, the desk from `battery-robot`, the published SO-ARM100 overhead webcam support, a fixed overhead RGB/RGB-D optical frame (assuming the use of a RealSense RGB-D cammera), and a physical-size 32 mm x 32 mm wrist-camera module. 

## Set up

This repository uses the same project-local `uv` layout as `battery-robot`. If `.tools/uv` is already present, install the locked environment with:

```bash
./uv.sh sync --locked
```

Otherwise install `uv` into `.tools/` first, or use a normal Python 3.12 virtual environment and install the project with `pip install -e .`.

On a Linux machine with a display, inspect the complete scene interactively:

```bash
./uv.sh run python simulation/view_scene.py
```

The viewer only refreshes the fixed keyframe; it never calls `mj_step`.

## Take camera photos

On a desktop session:

```bash
./uv.sh run python simulation/capture_cameras.py --depth
```

For headless Linux/EGL:

```bash
MUJOCO_GL=egl ./uv.sh run python simulation/capture_cameras.py --depth --overview
```

The command writes these artifacts under `outputs/camera-demo/`:

- `overhead_cam_rgb.png`: fixed overhead RGB view at 640 x 480.
- `wrist_cam_rgb.png`: wrist-mounted camera view from the stationary arm pose.
- `overhead_cam_depth_m.npy`: floating-point overhead depth in metres.
- `overhead_cam_depth_mm.png`: 16-bit depth in millimetres.
- `capture.json`: image dimensions, camera poses, FOVs, and filenames.

