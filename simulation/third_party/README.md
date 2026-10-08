# Third-party model provenance

## Robot Studio SO-101

The `robotstudio_so101` directory is carried from the `battery-robot` scene and
originates from MuJoCo Menagerie. Its bundled `LICENSE`, `README.md`,
`CHANGELOG.md`, and `UPSTREAM.txt` are retained.

Source revision recorded by `battery-robot`:
https://github.com/google-deepmind/mujoco_menagerie/tree/8161bba264d7fa7c99ca301e91e7fb44737676ad/robotstudio_so101

## SO-ARM100 overhead webcam support

The `so_arm100_overhead_webcam` directory contains the three unmodified STL
files and upstream README from:
https://github.com/TheRobotStudio/SO-ARM100/tree/main/Optional/Overhead_Cam_Mount_Webcam

The upstream Apache License 2.0 is retained as `LICENSE`. The scene supplies
only MuJoCo placement transforms and a generic camera shell; it does not modify
the STL files.

## User camera-mount assembly

`user_camera_mount/camera_mount_assembly.stl` and its STEP source were supplied
by this project owner (otavio-paz) after assembling the three SO-ARM100 support parts in
SolidWorks. The STL remains in millimetres and is scaled to metres by MJCF.
