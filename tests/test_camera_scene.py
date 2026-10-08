"""Structural checks for the stationary so-101 camera scene."""

from pathlib import Path
import sys
import unittest

import mujoco
import numpy as np


SIMULATION = Path(__file__).resolve().parents[1] / "simulation"
sys.path.insert(0, str(SIMULATION))

from capture_cameras import CAMERAS, load_static_scene  # noqa: E402


class CameraSceneTests(unittest.TestCase):
    """check the fixed hardware layout and saved pose"""

    def test_stationary_scene_has_expected_hardware(self) -> None:
        """confirm the scene has six joints, two cameras, and the expected pose."""
        model, data = load_static_scene()

        # five arm joints plus the gripper give six generalized positions
        self.assertEqual(model.nq, 6)

        # loading and forwarding the keyframe must not advance simulation time
        self.assertEqual(data.time, 0)
        self.assertTrue(np.isfinite(data.qpos).all())

        for camera in CAMERAS:
            self.assertGreaterEqual(
                mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_CAMERA, camera), 0
            )
        # these named geoms catch missing mount or camera assets at compile time
        for geom in (
            "camera_mount_assembly_geom",
            "overhead_camera_body",
            "overhead_camera_lens",
            "wrist_camera_board",
            "wrist_camera_lens",
        ):
            self.assertGreaterEqual(
                mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_GEOM, geom), 0
            )
        # the value includes the table-side station and arm-on-platform offsets
        np.testing.assert_allclose(
            data.body("base").xpos, [-.379058, .153430, .7597]
        )


if __name__ == "__main__":
    unittest.main()
