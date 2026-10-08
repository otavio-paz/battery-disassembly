"""Capture stationary rgb and optional depth images from the mujoco cameras"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import mujoco
import numpy as np
from PIL import Image


# these names must match the camera elements in camera_demo.xml
SCENE = Path(__file__).with_name("camera_demo.xml")
CAMERAS = ("overhead_cam", "wrist_cam")


def load_static_scene() -> tuple[mujoco.MjModel, mujoco.MjData]:
    """load the saved pose and update derived values without stepping physics."""
    model = mujoco.MjModel.from_xml_path(str(SCENE))
    data = mujoco.MjData(model)

    # using a named keyframe keeps captures repeatable when the xml changes
    key_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_KEY, "camera_demo")
    if key_id < 0:
        raise RuntimeError("camera_demo keyframe is missing")
    mujoco.mj_resetDataKeyframe(model, data, key_id)

    # mj_forward fills camera and body poses but does not advance data.time
    mujoco.mj_forward(model, data)
    return model, data


def render_rgb(
    model: mujoco.MjModel,
    data: mujoco.MjData,
    camera: str,
    width: int,
    height: int,
) -> np.ndarray:
    """render one rgb array from a named mjcf camera."""
    # the renderer size, rather than the camera's xml metadata, sets image size
    with mujoco.Renderer(model, height=height, width=width) as renderer:
        renderer.update_scene(data, camera=camera)
        return renderer.render().copy()


def render_depth(
    model: mujoco.MjModel,
    data: mujoco.MjData,
    camera: str,
    width: int,
    height: int,
) -> np.ndarray:
    """render metric depth from the same optical frame as the rgb image."""
    with mujoco.Renderer(model, height=height, width=width) as renderer:
        # depth mode changes the returned array from rgb bytes to float metres
        renderer.enable_depth_rendering()
        renderer.update_scene(data, camera=camera)
        return renderer.render().copy()


def render_overview(
    model: mujoco.MjModel,
    data: mujoco.MjData,
    width: int,
    height: int,
) -> np.ndarray:
    """render an external debug view that is not a simulated sensor."""
    # this free camera is only for checking placement in the full scene
    camera = mujoco.MjvCamera()
    camera.lookat[:] = (-.25, .10, .95)
    camera.distance = .82
    camera.azimuth = 135
    camera.elevation = -24
    with mujoco.Renderer(model, height=height, width=width) as renderer:
        renderer.update_scene(data, camera=camera)
        return renderer.render().copy()


def capture(
    output: Path,
    *,
    width: int = 640,
    height: int = 480,
    save_depth: bool = False,
    save_overview: bool = False,
) -> dict:
    """save both rgb views and optional depth without moving the arm."""
    if width <= 0 or height <= 0:
        raise ValueError("image dimensions must be positive")

    # one output directory keeps images and their metadata together
    output.mkdir(parents=True, exist_ok=True)
    model, data = load_static_scene()
    if data.time != 0:
        raise RuntimeError("the stationary capture scene unexpectedly advanced")

    manifest = {
        "scene": str(SCENE.resolve()),
        "simulation_time_s": float(data.time),
        "width": width,
        "height": height,
        "cameras": {},
    }
    for camera in CAMERAS:
        # fail early if a camera name was changed in xml but not here
        camera_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_CAMERA, camera)
        if camera_id < 0:
            raise RuntimeError(f"camera not found: {camera}")
        rgb = render_rgb(model, data, camera, width, height)
        rgb_file = f"{camera}_rgb.png"
        Image.fromarray(rgb).save(output / rgb_file)

        # the manifest records the exact world pose used for each image
        manifest["cameras"][camera] = {
            "rgb": rgb_file,
            "position_m": data.cam_xpos[camera_id].tolist(),
            "rotation_world_from_camera": data.cam_xmat[camera_id].reshape(3, 3).tolist(),
            "vertical_fov_deg": float(model.cam_fovy[camera_id]),
        }

    if save_depth:
        # keep float metres for calculations and a 16-bit png for inspection
        depth = render_depth(model, data, "overhead_cam", width, height)
        np.save(output / "overhead_cam_depth_m.npy", depth)
        depth_mm = np.clip(np.nan_to_num(depth, nan=0, posinf=0, neginf=0) * 1000, 0, 65535).astype(np.uint16)
        Image.fromarray(depth_mm).save(output / "overhead_cam_depth_mm.png")
        manifest["cameras"]["overhead_cam"].update({
            "depth_m": "overhead_cam_depth_m.npy",
            "depth_mm_png": "overhead_cam_depth_mm.png",
        })

    if save_overview:
        # the overview helps with setup but is not part of the robot observation
        overview_file = "scene_overview.png"
        Image.fromarray(render_overview(model, data, width, height)).save(
            output / overview_file
        )
        manifest["debug_overview"] = overview_file

    # write the manifest last so it describes files that already exist
    (output / "capture.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def main() -> None:
    """parse command-line options and run one stationary capture."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=SCENE.parents[1] / "outputs" / "camera-demo",
    )
    parser.add_argument("--width", type=int, default=640)
    parser.add_argument("--height", type=int, default=480)
    parser.add_argument(
        "--depth",
        action="store_true",
        help="also save overhead metric depth as npy and a 16-bit millimetre png.",
    )
    parser.add_argument(
        "--overview",
        action="store_true",
        help="also save an external debug view of the arm and camera support.",
    )
    args = parser.parse_args()
    manifest = capture(
        args.output,
        width=args.width,
        height=args.height,
        save_depth=args.depth,
        save_overview=args.overview,
    )
    print(json.dumps(manifest, indent=2))
    print(f"images saved to {args.output.resolve()}")


if __name__ == "__main__":
    main()
