import carb
import math
from pathlib import Path
from pxr import Usd, UsdLux, UsdGeom, Sdf, Gf, Vt, UsdPhysics, PhysxSchema
import sys
#put schemaHelpers.py into path
from .schemaHelpers import PhysxParticleInstancePrototype, \
     addPhysxParticleSystem, addPhysxParticlesSimple
import omni.timeline

from typing import List
import math

from .utils import generate_cylinder_y, point_sphere
from .constants import PARTICLE_PROPERTY, particel_scale
from omni.physx.scripts import particleUtils, physicsUtils

def setGridFilteringPass(gridFilteringFlags: int, passIndex: int, operation: int, numRepetitions: int = 1):
    """
    set grid filtering pass
    """
    numRepetitions = max(0, numRepetitions - 1)
    shift = passIndex * 4
    gridFilteringFlags &= ~(3 << shift)
    gridFilteringFlags |= (((operation) << 2) | numRepetitions) << shift
    return gridFilteringFlags

class Faucet():
    def __init__(self,
        material_name = "OmniSurface_ClearWater", inflow_path:str = "/World/faucet/inflow", 
        link_paths:List[str] = ["/World/faucet/link_0"]
         ):
        """! Faucet class
         @param particle_params : parameters for particles
         @param iso_surface_params: parameters for iso_surface
         @param liquid_material_path: parameters for liquid materials
         @param inflow_path: used to compute the location of water drops
         @param link_paths: used to compute the rotation of faucet handle and determine the speed and size of water drops
         @param particle_params: parameters related to particle systems
         @return an instance of Faucet class
        """
        self.material_name = material_name

        # inflow position
        self.stage = omni.usd.get_context().get_stage()
        self.inflow_path = inflow_path
        self.inflow_prim = self.stage.GetPrimAtPath(inflow_path)
        assert self.inflow_prim.IsValid(), "inflow_path is not valid"
        mat = omni.usd.utils.get_world_transform_matrix(self.inflow_prim) 
        
        self.inflow_position = Gf.Vec3f(*mat.ExtractTranslation())
    

    def point_sphere(self, samples, scale):
        """! create locations for each particles
        @param samples: the number of particles per sphere
        @param scale: the scale(radius) of the water drop 
        """
        indices = [x + 0.5 for x in range(0, samples)]

        phi = [math.acos(1 - 2 * x / samples) for x in indices]
        theta = [math.pi * (1 + 5**0.5) * x for x in indices]

        x = [math.cos(th) * math.sin(ph) * scale for (th, ph) in zip(theta, phi)]
        y = [math.sin(th) * math.sin(ph) * scale for (th, ph) in zip(theta, phi)]
        z = [math.cos(ph) * scale for ph in phi]
        points = [Gf.Vec3f(x, y, z) for (x, y, z) in zip(x, y, z)]
        return points
    
    def set_up_cylinder_particles(self, cylinder_height, cylinder_radius):
        """
        Set up particle system
        ::param cylinder_height: the height of the cylinder
        ::param cylinder_radius: the radius of the cylinder
        """

        self.particleInstanceStr_tmp = self.particleInstanceStr  + "/particlesInstance"
        particleInstancePath = omni.usd.get_stage_next_free_path(self.stage, self.particleInstanceStr_tmp, False)
        particleInstancePath = Sdf.Path(particleInstancePath)

        proto = PhysxParticleInstancePrototype()
        proto.selfCollision = True
        proto.fluid = True
        proto.collisionGroup = 0
        proto.mass = PARTICLE_PROPERTY._particle_mass
        protoArray = [proto]

        positions_list = []
        velocities_list = []
        protoIndices_list = []

        # lowerCenter =  Gf.Vec3f(0, 0, 0) # self.inflow_position
        lowerCenter = self.inflow_position

        particle_rest_offset = self._particleSystemSchemaParameters["fluid_rest_offset"]
    
        positions_list = generate_cylinder_y(lowerCenter, h=cylinder_height, radius=cylinder_radius, sphereDiameter=particle_rest_offset * 4.0)
     
        for _ in range(len(positions_list)):
            velocities_list.append(Gf.Vec3f(0, 0, 0))
            protoIndices_list.append(0)

        # print("positions_list", len(positions_list))
        self.positions_list = positions_list
        protoIndices =Vt.IntArray(protoIndices_list)
        positions =Vt.Vec3fArray(positions_list)
        velocities =Vt.Vec3fArray(velocities_list)
        widths_list = [particle_rest_offset * 4] * len(positions_list)

        print("particleInstancePath", particleInstancePath.pathString)
        # add_physx_particleset_pointinstancer
        particleUtils.add_physx_particleset_points(  
                stage = self.stage,
                path = particleInstancePath,
                positions_list = positions,
                velocities_list = velocities,
                widths_list = widths_list,
                particle_system_path = self.particleSystemPath,
                self_collision=True,
                fluid=True,
                particle_group=0,
                particle_mass=PARTICLE_PROPERTY._particle_mass,
                density=0.0,
            )

        # prototypePath = particleInstancePath.pathString + "/particlePrototype0"
        

        # sphere = UsdGeom.Sphere.Define(self.stage, Sdf.Path(prototypePath))
        # spherePrim = sphere.GetPrim()
        # # spherePrim.GetAttribute('visibility').Set('invisible')
        # color_rgb = [207/255.0, 244/255.0, 254/255.0]
        # color =Vt.Vec3fArray([Gf.Vec3f(color_rgb[0], color_rgb[1], color_rgb[2])])
        # sphere.CreateDisplayColorAttr(color)

        # spherePrim.CreateAttribute("enableAnisotropy", Sdf.ValueTypeNames.Bool, True).Set(True)


    def set_up_fluid_particle_system(self, instance_index = 0):
        """
        Fluid / PhysicsScene
        """

        self.stage = omni.usd.get_context().get_stage()
        
        self.physicsScenePath = "/World/physicsScene"
        self.particleSystemPath = Sdf.Path(f"/World/Fluid/particleSystem{instance_index}")
        
        self.particleInstanceStr = f"/World/Fluid/particleSystem{instance_index}"

        # print("particleInstanceStr", self.particleInstanceStr)


        # # Physics scene
        # self._gravityMagnitude = gravityMagnitude  
        # self._gravityDirection = Gf.Vec3f(0.0, 0.0, -1.0)
        if self.stage.GetPrimAtPath('/World/physicsScene'):
            scene = UsdPhysics.Scene.Get(self.stage, self.physicsScenePath)
        else:
            scene = UsdPhysics.Scene.Define(self.stage, self.physicsScenePath)
        # scene.CreateGravityDirectionAttr().Set(self._gravityDirection)
        # scene.CreateGravityMagnitudeAttr().Set(self._gravityMagnitude)
        # physxSceneAPI = PhysxSchema.PhysxSceneAPI.Apply(scene.GetPrim())
        # physxSceneAPI.CreateEnableCCDAttr().Set(True)
        # physxSceneAPI.GetTimeStepsPerSecondAttr().Set(120)



        self._fluidSphereDiameter = PARTICLE_PROPERTY._fluidSphereDiameter #0.24
        
        # solver parameters:
        # self._solverPositionIterations = 10
        # self._solverVelocityIterations = 10
        
        # self._particleSystemSchemaParameters = {
        #     "contact_offset": 0.3,
        #     "particle_contact_offset": 0.25,
        #     "rest_offset": 0.25,
        #     "solid_rest_offset": 0,
        #     "fluid_rest_offset": 0.5 * self._fluidSphereDiameter + 0.03,
        #     "solver_position_iterations": self._solverPositionIterations,
        #     "solver_velocity_iterations": self._solverVelocityIterations,
        #     "wind": Gf.Vec3f(0, 0, 0),
        # }

        self._particleSystemSchemaParameters = PARTICLE_PROPERTY._particleSystemSchemaParameters

        # self._particleSystemAttributes = {
        #     "cohesion": 7.4,
        #     "smoothing": 0.8,
        #     "anisotropyScale": 1.0,
        #     "anisotropyMin": 0.2,
        #     "anisotropyMax": 2.0,
        #     "surfaceTension": 2.0, #0.74,
        #     "vorticityConfinement": 0.5,
        #     "viscosity": 5.0,
        #     "particleFriction": 0.34,
        #     "maxParticles": 20000,
        # }

        self._particleSystemAttributes = PARTICLE_PROPERTY._particleSystemAttributes
        self._particleSystemAttributes["maxParticles"] = 2000
        self._particleSystemAttributes["viscosity"] = 0.001
        self._particleSystem = particleUtils.add_physx_particle_system(
                self.stage, self.particleSystemPath, **self._particleSystemSchemaParameters, simulation_owner=Sdf.Path(self.physicsScenePath)
            )
        
        particleSystem = self.stage.GetPrimAtPath(self.particleSystemPath)

        # Render material
        mtl_created = []
        omni.kit.commands.execute(
            "CreateAndBindMdlMaterialFromLibrary",
            mdl_name="OmniSurfacePresets.mdl",
            mtl_name=self.material_name,
            mtl_created_list=mtl_created,
        )
        mtl_path = mtl_created[0]
        omni.kit.commands.execute("BindMaterial", prim_path=self.particleSystemPath, material_path=mtl_path)

        # Create a pbd particle material and set it on the particle system
        particleUtils.add_pbd_particle_material(self.stage, mtl_path, cohesion=0.3, friction=0.15, viscosity=20.0, surface_tension=0.074, cfl_coefficient=1.0)
        physicsUtils.add_physics_material_to_prim(self.stage, particleSystem, mtl_path)
        
        # add particle anisotropy
        anisotropyAPI = PhysxSchema.PhysxParticleAnisotropyAPI.Apply(particleSystem)
        anisotropyAPI.CreateParticleAnisotropyEnabledAttr().Set(True)
        aniso_scale = 2.5
        anisotropyAPI.CreateScaleAttr().Set(aniso_scale)
        anisotropyAPI.CreateMinAttr().Set(0.3*aniso_scale)
        anisotropyAPI.CreateMaxAttr().Set(1.5*aniso_scale)

        # add particle smoothing
        smoothingAPI = PhysxSchema.PhysxParticleSmoothingAPI.Apply(particleSystem)
        smoothingAPI.CreateParticleSmoothingEnabledAttr().Set(True)
        smoothingAPI.CreateStrengthAttr().Set(0.5)

        # apply isosurface params
        fluidRestOffset = self._particleSystemSchemaParameters["fluid_rest_offset"]
        isosurfaceAPI = PhysxSchema.PhysxParticleIsosurfaceAPI.Apply(particleSystem)
        isosurfaceAPI.CreateIsosurfaceEnabledAttr().Set(True)
        isosurfaceAPI.CreateMaxVerticesAttr().Set(1024 * 1024)
        isosurfaceAPI.CreateMaxTrianglesAttr().Set(2 * 1024 * 1024)
        isosurfaceAPI.CreateMaxSubgridsAttr().Set(1024 * 4)
        #isosurfaceAPI.CreateGridSpacingAttr().Set(fluidRestOffset*0.9)
        #isosurfaceAPI.CreateSurfaceDistanceAttr().Set(fluidRestOffset*0.95)
        # isosurfaceAPI.CreateGridFilteringPassesAttr().Set("GS")
        isosurfaceAPI.CreateGridSmoothingRadiusAttr().Set(fluidRestOffset*1.0)
        isosurfaceAPI.CreateNumMeshSmoothingPassesAttr().Set(4)
        isosurfaceAPI.CreateNumMeshNormalSmoothingPassesAttr().Set(4)

        # primVarsApi = UsdGeom.PrimvarsAPI(particleSystem)
        # primVarsApi.CreatePrimvar("doNotCastShadows", Sdf.ValueTypeNames.Bool).Set(True)

        # filterSmooth = 1
        # filtering = 0
        # passIndex = 0
        # filtering = setGridFilteringPass(filtering, passIndex, filterSmooth)
        # passIndex = passIndex + 1
        # filtering = setGridFilteringPass(filtering, passIndex, filterSmooth)
        # passIndex = passIndex + 1
        # self.iso_surface_params = {
        #     "maxIsosurfaceVertices": [Sdf.ValueTypeNames.Int, True,  1024 * 1024],
        #     "maxIsosurfaceTriangles": [Sdf.ValueTypeNames.Int, True, 2 * 1024 * 1024],
        #     "maxNumIsosurfaceSubgrids": [Sdf.ValueTypeNames.Int, True,  1024 * 4],
        #     "isosurfaceGridSpacing": [Sdf.ValueTypeNames.Float, True, 0.2],
        #     "isosurfaceKernelRadius": [Sdf.ValueTypeNames.Float, True,  0.5 ], 
        #     "isosurfaceLevel": [ Sdf.ValueTypeNames.Float, True, -0.3 ],
        #     "isosurfaceGridFilteringFlags": [Sdf.ValueTypeNames.Int, True, filtering ],
        #     "isosurfaceGridSmoothingRadiusRelativeToCellSize": [Sdf.ValueTypeNames.Float, True, 0.3 ],
        #     "isosurfaceEnableAnisotropy": [Sdf.ValueTypeNames.Bool, True, False ],
        #     "isosurfaceAnisotropyMin": [ Sdf.ValueTypeNames.Float, True, 0.1 ],
        #     "isosurfaceAnisotropyMax": [ Sdf.ValueTypeNames.Float, True, 2.0 ],
        #     "isosurfaceAnisotropyRadius": [ Sdf.ValueTypeNames.Float, True, 0.5 ],
        #     "numIsosurfaceMeshSmoothingPasses": [ Sdf.ValueTypeNames.Int,  True, 5 ],
        #     "numIsosurfaceMeshNormalSmoothingPasses": [ Sdf.ValueTypeNames.Int, True, 5 ],
        #     "isosurfaceDoNotCastShadows": [Sdf.ValueTypeNames.Bool, True, True ]
        # }
        # particleSystem.CreateAttribute("enableIsosurface", Sdf.ValueTypeNames.Bool, True).Set(True)
        # for key,value in self.iso_surface_params.items():
        #         if isinstance(value, list):
        #             particleSystem.CreateAttribute(key, value[0], value[1]).Set(value[2])
        #         else:
        #             particleSystem.GetAttribute(key).Set(value)

        # self.stage.SetInterpolationType(Usd.InterpolationTypeHeld)  

    def _setup_callbacks(self):
        """! callbacks registered with timeline and physics steps to drop water 
        """
        # callbacks
        self._timeline = omni.timeline.get_timeline_interface()
        stream = self._timeline.get_timeline_event_stream()
        self._timeline_subscription = stream.create_subscription_to_pop(self._on_timeline_event)
        # subscribe to Physics updates:
        self._physics_update_subscription = omni.physx.get_physx_interface().subscribe_physics_step_events(
            self.on_physics_step
        )

        # events = omni.physx.get_physx_interface().get_simulation_event_stream()
        # self._simulation_event_sub = events.create_subscription_to_pop(self._on_simulation_event)

    def _on_timeline_event(self, e):
        if e.type == int(omni.timeline.TimelineEventType.STOP):
            self.it = 0
            self._physics_update_subscription = None
            self._timeline_subscription = None

    def on_physics_step(self, dt):
        xformCache = UsdGeom.XformCache()

        # compute location to dispense water
        pose =  xformCache.GetLocalToWorldTransform(self.stage.GetPrimAtPath(self.inflow_path))
        pos_faucet = Gf.Vec3f(pose.ExtractTranslation())

        ##TODO hangle multiple faucet handles
        
        rate = 0.2 # self.rate_checkers[0].compute_distance()/100.0
        
        if rate > 1:
            rate = 1
      
        # if self.it == 0:
        #     iso2Prim = self.stage.GetPrimAtPath(self.particleSystemPath.pathString +"/Isosurface")
        #     rel = iso2Prim.CreateRelationship("material:binding", False)
        #     # rel.SetTargets([Sdf.Path(self.liquid_material_path)])
        #     rel.SetTargets([Sdf.Path("/World/game/other_Basin_1/Looks/OmniSurface_ClearWater")])

        #TODO we can have the water keep running, but we should delete some particles that are too old and not in containers.
        #this implementation will stop after 200 balls

        if self.it > 200:
            return
        
        if rate < 0.1:
            return

         # emit a ball based on rate
        rate = min(0.35, rate)
        if (self.counter < 100 - rate*200 ):
            self.counter = self.counter + 1
            return
     
        self.counter = 0
        self.it = self.it + 1


        # self.create_ball(rate)

    def __del__(self):
        self._physics_update_subscription = None
        self._timeline_subscription = None



