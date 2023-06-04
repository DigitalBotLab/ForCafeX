import omni.ext
import omni.ui as ui
import omni.timeline
import omni.kit.app
import carb
import numpy as np
import asyncio

# UI
from .ui.style import julia_modeler_style
from .ui.custom_multifield_widget import CustomMultifieldWidget
from .ui.custom_bool_widget import CustomBoolWidget


# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class CafexRobotControlExtension(omni.ext.IExt):
    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    def on_startup(self, ext_id):
        print("[dbl.for.blendid] dbl for blendid startup")

        # set up fps limit
        carb.settings.get_settings().set_float("/app/runLoops/main/rateLimitFrequency", 25) 
        carb.settings.get_settings().set_float("/app/runLoops/present/rateLimitFrequency", 25) 
        carb.settings.get_settings().set_bool("/rtx/ecoMode/enabled", True)
    
        self._window = ui.Window("For CafeX", width=300, height=300)
        with self._window.frame:
            with ui.VStack():
                ui.Button("Demo 1", height = 20, clicked_fn=self.demo1)
                ui.Button("Demo 2", height = 20, clicked_fn=self.demo2)
                
                ui.Line(height = 6)
                ui.Button("Add Fluid", height = 20, clicked_fn=self.fluid_test)
                ui.Button("Register Physics Event", height = 50, clicked_fn=self.register_physics_event)
                with ui.HStack(height = 20): 
                    ui.Label("Robot Prim Path:", width = 200)
                    self.robot_path_widget = ui.StringField(width = 300)
                    self.robot_path_widget.model.set_value("/World/denso_v6_rg2/denso")
                
                ui.Spacer(height = 9)
                ui.Label("End Effector", height = 20)
                with ui.HStack(height = 20):
                    self.ee_pos_widget = CustomMultifieldWidget(
                        label="Transform",
                        default_vals=[0.4, 0.2, 0.3],
                        height = 20,
                    )
                ui.Spacer(height = 9)
                with ui.HStack(height = 20):
                    self.ee_ori_widget = CustomMultifieldWidget(
                        label="Orient (Euler)",
                        default_vals=[0, 0.0, 0],
                        height = 20,
                    )
                ui.Spacer(height = 9)
                ui.Button("Update EE Target", height = 20, clicked_fn=self.update_ee_target)
                ui.Button("Open/Close Gripper", height = 20, clicked_fn=self.toggle_gripper)

                ui.Spacer(height = 9)
                ui.Line(height = 2)
                with ui.HStack(height = 20):
                    self.joint_read_widget = CustomMultifieldWidget(
                        label="Joint Angle (read only):",
                        sublabels=["j1", "j2", "j3", "j4", "j5", "j6"],
                        default_vals=[0.0] * 7,
                        read_only= True
                    )
                    
                with ui.HStack(height = 20):
                    self.ee_pos_read_widget = CustomMultifieldWidget(
                        label="EE Position(read only):",
                        sublabels=["x", "y", "z"],
                        default_vals=[0, 0, 0],
                        read_only= True
                    )

                with ui.HStack(height = 20):
                    self.ee_ori_quat_read_widget = CustomMultifieldWidget(
                        label="EE Quaternion(read only):",
                        sublabels=[ "w", "x", "y", "z"],
                        default_vals=[1, 0, 0, 0],
                        read_only= True
                    )

        # robot
        self.robot = None
        self.controller = None  
        self.event_t = 0.0

        # stream
        self._is_stopped = True
        self._tensor_started = False   

    def on_shutdown(self):
        print("[dbl.for.blendid] dbl for blendid shutdown")

    ########################## events #######################################################
    def register_physics_event(self):
        print("register_physics_event")
        
        # timeline
        stream = omni.timeline.get_timeline_interface().get_timeline_event_stream()
        self._timeline_sub = stream.create_subscription_to_pop(self._on_timeline_event)

    def _on_timeline_event(self, event):
        if event.type == int(omni.timeline.TimelineEventType.PLAY):
            self._physics_update_sub = omni.physx.get_physx_interface().subscribe_physics_step_events(self._on_physics_step)
            self._is_stopped = False

        elif event.type == int(omni.timeline.TimelineEventType.STOP):
            self._physics_update_sub = None
            self._timeline_sub = None

            self._is_stopped = True
            self._tensor_started = False

            self.robot = None
            self.controller = None  
        

    def _can_callback_physics_step(self) -> bool:
        if self._is_stopped:
            return False

        if self._tensor_started:
            return True

        self._tensor_started = True
        self.set_robot()
        return True 
    
    def _on_physics_step(self, dt):
        self.event_t += dt # update time

        if not self._can_callback_physics_step():
            return

        if self.controller:
            # print("_on_physics_step")
            self.controller.forward()


            if self.event_t >= 1.0:
                # update joint info 
                self.update_robot_ui()
                self.event_t = 0.0
    
    ########################### robot #######################################################
    def set_robot(self, go_home=True):
        print("set_robot")

        from .denso.robot import MyRobot
        from .denso.robot_config import DENSO_ROBOT_CONFIG
        # set robot
        prim_path = self.robot_path_widget.model.as_string
        self.robot = MyRobot(prim_path = prim_path, 
                                end_effector_path="/World/denso_v6_rg2/onrobot/onrobot_rg2_base_link",
                                gripper_dof_names = DENSO_ROBOT_CONFIG["gripper_dof_names"],
                                gripper_open_position=DENSO_ROBOT_CONFIG["gripper_open_position"],
                                gripper_closed_position=DENSO_ROBOT_CONFIG["gripper_closed_position"],
                    )
        self.robot.initialize()
        print("robot_info", self.robot.num_dof)
        print("robot_dof_names", len(self.robot.dof_names), self.robot.dof_names)
        print("robot_gripper", self.robot.gripper._gripper_joint_num)

        # # set controller
        from .denso.controller import MyController
        self.controller = MyController("denso_controller", self.robot, connect_server=False)

        if go_home:
            from .denso.action_config import action_config
            self.controller.apply_high_level_action(action_config["go_home"])

    def update_ee_target(self):
        print("update_ee_target")
        from .denso.numpy_utils import euler_angles_to_quat
        if self.controller:
            self.controller.update_event("move")
            # current_pos, current_rot = self.robot.end_effector.get_world_pose()
            pos = [self.ee_pos_widget.multifields[i].model.as_float for i in range(3)]
            rot = [self.ee_ori_widget.multifields[i].model.as_float for i in range(3)]
            
            pos =  np.array(pos) # + np.array(current_pos)
            rot = euler_angles_to_quat(rot, degrees=True) # xyzw
            # current_rot = np.array([current_rot[1], current_rot[2], current_rot[3], current_rot[0]])
            # rot = quat_mul(current_rot, rot)
            rot = np.array([rot[3], rot[0], rot[1], rot[2]]) # wxyz

            print("updating controller ee target:", pos, rot)
            self.controller.update_ee_target(pos, rot)

    def toggle_gripper(self):
        print("Toggle Gripper")
        if self.controller:
            event = "open" if self.controller.event == "close" else "close"
            self.controller.update_event(event) 
    
    ######################### ui #############################################################
    def update_robot_ui(self):
        """
        read robot joint angles and update ui
        """
        assert self.robot, "robot is not initialized"
        joint_angles = self.robot.get_joint_positions()
        joint_angles = [np.rad2deg(joint_angles[i]) for i in range(self.robot.num_dof)]
        self.joint_read_widget.update(joint_angles)
        self.ee_pos_read_widget.update(self.robot.end_effector.get_world_pose()[0])
        rot_quat = self.robot.end_effector.get_world_pose()[1]
        self.ee_ori_quat_read_widget.update(rot_quat)
        # rot_euler = quat_to_euler_angles(rot_quat, degrees=True)
        # print("rot_euler:", rot_euler)
        # self.ee_ori_euler_read_widget.update(rot_euler[0])

    ################################ fluid #########################################################
    def fluid_test(self):
        print(f"[dbl.for.blendid] debug")
         #"/World/Xform"
        from .fluid.faucet import Faucet
        # faucet = Faucet(inflow_path = inflow_path)
        # faucet.set_up_fluid_particle_system()
        # faucet.set_up_cylinder_particles(cylinder_height=1.5, cylinder_radius=0.02)

        faucet = Faucet(material_name = "OmniSurface_ClearWater", 
                        inflow_path = "/World/WorkingArea/MainBoard/CoffeePoint",
                        material_path="/World/Looks/OmniSurface_Coffee") # "/World/Looks/OmniSurface_OrangeJuice" # "/World/Looks/OmniSurface_Coffee"
        faucet.set_up_fluid_particle_system(instance_index=1)
        faucet.set_up_cylinder_particles(cylinder_height=6.0, cylinder_radius=0.015, z_offset=0.2)

    ####################### debug ############################################################
    def demo1(self):
        # from pxr import UsdGeom
        # unit = UsdGeom.GetStageMetersPerUnit(omni.usd.get_context().get_stage())
        # print("stage unit", unit)
        if self.controller: 
            from .denso.action_config import action_config
            ## Test 0
            # self.controller.apply_high_level_action(action_config["low_level_test"])
            
            # # Test 1
            # self.controller.apply_high_level_action(action_config["pick_up_cup"])
            # self.controller.apply_high_level_action(action_config["go_home_reverse"])
            # self.controller.apply_high_level_action(action_config["place_cup_to_coffee_point"])
            # self.controller.apply_high_level_action(action_config["move_cup_out_coffee_point"])
            # self.controller.apply_high_level_action(action_config["go_home_reverse"])
            # self.controller.apply_high_level_action(action_config["place_cup_to_milk_point"])

            ## Test 2
            self.controller.apply_high_level_action(action_config["move_cup_out_coffee_point"])

    def demo2(self):
        # from pxr import UsdGeom
        # unit = UsdGeom.GetStageMetersPerUnit(omni.usd.get_context().get_stage())
        # print("stage unit", unit)
        if self.controller: 
            from .denso.action_config import action_config
            ## Test 0
            # self.controller.apply_high_level_action(action_config["low_level_test"])
            
            # Test 1
            self.controller.apply_high_level_action(action_config["pick_up_cup"])
            self.controller.apply_high_level_action(action_config["go_home_reverse"])
            

    def on_shutdown(self):
        print("[cafex.robot.control] cafex robot control shutdown")
