"""Open the stationary SO-101 camera scene in the interactive mujoco viewer"""

from __future__ import annotations

import time

from mujoco import viewer

from capture_cameras import load_static_scene


def main() -> None:
    """show the saved pose until the viewer window is closed."""
    model, data = load_static_scene()
    with viewer.launch_passive(model, data) as window:
        # these values only control the viewer and do not change sensor cameras
        window.cam.lookat[:] = (0.10, 0.10, 0.84)
        window.cam.distance = 1.15
        window.cam.azimuth = 135
        window.cam.elevation = -24
        while window.is_running():
            # present the unchanged keyframe without calling mj_step
            window.sync()
            time.sleep(1 / 30)


if __name__ == "__main__":
    main()
