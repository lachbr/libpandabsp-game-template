from panda3d.bsp import CAMERA_MAIN, CAMERA_COMPUTE, CAMERA_SHADOW, BSPLoader, Audio3DManager, BSPRender, BSPShaderGenerator
from panda3d.core import NodePath, OmniBoundingVolume, Vec3, Vec4, RescaleNormalAttrib, LightRampAttrib

from direct.showbase.ShowBase import ShowBase
from direct.directnotify.DirectNotifyGlobal import directNotify

from src.bsp.BSPPostProcess import BSPPostProcess

class BSPBase(ShowBase):
    
    notify = directNotify.newCategory("BSPBase")

    def __init__(self, *args, **kwargs):
        ShowBase.__init__(self, *args, **kwargs)
        
        from panda3d.core import RenderAttribRegistry
        from panda3d.core import ShaderAttrib, TransparencyAttrib
        from panda3d.bsp import BSPMaterialAttrib
        attribRegistry = RenderAttribRegistry.getGlobalPtr()
        attribRegistry.setSlotSort(BSPMaterialAttrib.getClassSlot(), 0)
        attribRegistry.setSlotSort(ShaderAttrib.getClassSlot(), 1)
        attribRegistry.setSlotSort(TransparencyAttrib.getClassSlot(), 2)
        
        gsg = self.win.getGsg()
            
        # Let's print out the Graphics information.
        self.notify.info('Graphics Information:\n\tVendor: {0}\n\tRenderer: {1}\n'
                        '\tVersion: {2}\n\tSupports Cube Maps: {3}\n'
                        '\tSupports 3D Textures: {4}\n\tSupports Compute Shaders: {5}'
                         .format(gsg.getDriverVendor(), 
                                 gsg.getDriverRenderer(), 
                                 gsg.getDriverVersion(), 
                                 str(gsg.getSupportsCubeMap()), 
                                 str(gsg.getSupports3dTexture()), 
                                 str(gsg.getSupportsComputeShaders())))
                                 
        # Enable shader generation on all of the main scenes
        if gsg.getSupportsBasicShaders() and gsg.getSupportsGlsl():
            self.render.setShaderAuto()
            self.render2d.setShaderAuto()
            self.render2dp.setShaderAuto()
            self.aspect2d.setShaderAuto()
            self.pixel2d.setShaderAuto()
        else:
            # I don't know how this could be possible
            self.notify.error("GLSL shaders unsupported by graphics driver.")
            return
            
        self.camNode.setCameraMask(CAMERA_MAIN)
        
        # Any ComputeNodes should be parented to this node, not render.
        # We isolate ComputeNodes to avoid traversing the same ComputeNodes
        # when doing multi-pass rendering.
        self.computeRoot = NodePath('computeRoot')
        self.computeCam = self.makeCamera(self.win)
        self.computeCam.node().setCameraMask(CAMERA_COMPUTE)
        self.computeCam.node().setCullBounds(OmniBoundingVolume())
        self.computeCam.node().setFinal(True)
        self.computeCam.reparentTo(self.computeRoot)
        
        self.bspLoader = None
        self.bspLevel = None
        self.brushCollisionMaterialData = {}
        self.createBSPLoader()
        
        self.audio3d = None
        self.create3DAudio()
        
        # Initialized in createShaderGenerator()
        self.shaderGenerator = None
        
        # Initialized in createPostProcess()
        self.filters = None
        
        self.render.show(CAMERA_SHADOW)
        self.render.setAttrib(LightRampAttrib.makeIdentity())
        
    def create3DAudio(self):
        # Setup 3d audio                                 run before igLoop so 3d positioning doesn't lag behind
        self.audio3d = Audio3DManager(self.sfxManagerList[0], self.camera, self.render, 40)
        self.audio3d.setDropOffFactor(0.15)
        self.audio3d.setDopplerFactor(0.15)
        
    def createBSPLoader(self):
        self.bspLoader = BSPLoader.getGlobalPtr()
        self.bspLoader.setGamma(2.2)
        self.bspLoader.setWin(self.win)
        self.bspLoader.setCamera(self.camera)
        self.bspLoader.setRender(self.render)
        self.bspLoader.setMaterialsFile("phase_14/etc/materials.txt")
        self.bspLoader.setWantVisibility(True)
        self.bspLoader.setVisualizeLeafs(False)
        self.bspLoader.setWantLightmaps(True)
        self.bspLoader.setWantShadows(self.config.GetBool("want-pssm", True))
        
    def createPostProcess(self):
        self.filters = BSPPostProcess()
        self.filters.addCamera(self.cam)
        self.filters.setup()
        
    def createShaderGenerator(self):
        self.shaderGenerator = BSPShaderGenerator(self.win.getGsg(), self.camera, self.render)
        self.win.getGsg().setShaderGenerator(self.shaderGenerator)
        self.shaderGenerator.startUpdate()
        
        # Register the shaders that can be used in a BSPMaterial
        from panda3d.bsp import (VertexLitGenericSpec, UnlitGenericSpec, LightmappedGenericSpec,
                                 UnlitNoMatSpec, CSMRenderSpec, SkyBoxSpec, DecalModulateSpec)
        
        vlg = VertexLitGenericSpec()    # models
        ulg = UnlitGenericSpec()        # ui elements, particles, etc
        lmg = LightmappedGenericSpec()  # brushes, displacements
        unm = UnlitNoMatSpec()          # when there's no material
        csm = CSMRenderSpec()           # renders the shadow scene for CSM
        skb = SkyBoxSpec()              # renders the skybox onto faces
        dcm = DecalModulateSpec()       # blends decals
        
        self.shaderGenerator.addShader(vlg)
        self.shaderGenerator.addShader(ulg)
        self.shaderGenerator.addShader(unm)
        self.shaderGenerator.addShader(lmg)
        self.shaderGenerator.addShader(csm)
        self.shaderGenerator.addShader(skb)
        self.shaderGenerator.addShader(dcm)
        
    def convertHammerAngles(self, angles):
        """
        (pitch, yaw + 90, roll) -> (yaw, pitch, roll)
        """
        temp = angles[0]
        angles[0] = angles[1] - 90
        angles[1] = temp
        return angles
        
    def getBSPLevelLightEnvironmentData(self):
        #    [has data, angles, color]
        data = [0, Vec3(0), Vec4(0)]
        
        if not self.bspLoader.hasActiveLevel():
            return data
        
        for i in xrange(self.bspLoader.getNumEntities()):
            classname = self.bspLoader.getEntityValue(i, "classname")
            if classname == "light_environment":
                data[0] = 1
                data[1] = self.convertHammerAngles(
                    self.bspLoader.getEntityValueVector(i, "angles"))
                data[2] = self.bspLoader.getEntityValueColor(i, "_light")
                break
                
        return data
        
    def setupRender(self):
        """
        Creates the render scene graph, the primary scene graph for
        rendering 3-d geometry.
        """
        ## This is the root of the 3-D scene graph.
        ## Make it a BSPRender node to automatically cull
        ## nodes against the BSP leafs if there is a loaded
        ## BSP level.
        self.render = NodePath(BSPRender('render', BSPLoader.getGlobalPtr()))
        self.render.setAttrib(RescaleNormalAttrib.makeDefault())
        self.render.setTwoSided(0)
        self.backfaceCullingEnabled = 1
        self.textureEnabled = 1
        self.wireframeEnabled = 0
        
    def doNextFrame(self, func, extraArgs = []):
        taskMgr.add(self.__doNextFrameTask, "doNextFrame" + str(id(func)), extraArgs = [func, extraArgs], appendTask = True, sort = 100000)

    def __doNextFrameTask(self, func, extraArgs, task):
        func(*extraArgs)
        return task.done
        
    def loadSfxOnNode(self, sndFile, node):
        """ Loads up a spatialized sound and attaches it to the specified node. """
        snd = self.audio3d.loadSfx(sndFile)
        self.audio3d.attachSoundToObject(snd, node)
        return snd
        
    def renderFrames(self):
        self.graphicsEngine.renderFrame()
        self.graphicsEngine.renderFrame()
        
    def renderFrameAndSync(self):
        self.graphicsEngine.renderFrame()
        self.graphicsEngine.syncFrame()

    def prepareScene(self):
        self.render.prepareScene(self.win.getGsg())
        
    def cleanupBSPLevel(self):
        if self.bspLevel:
            # Cleanup any physics meshes for the level.
            self.bspLevel.removeNode()
        self.bspLevel = None
        self.bspLoader.cleanup()
        base.brushCollisionMaterialData = {}
        
    def loadBSPLevel(self, mapFile):
        self.cleanupBSPLevel()
        
        self.bspLoader.read(mapFile)
        self.bspLevel = self.bspLoader.getResult()
        self.bspLoader.doOptimizations()
        
        self.shaderGenerator.setIdentityCubemap(loader.loadCubeMap("materials/sky/sky#.png"))
        
        self.bspLevel.reparentTo(self.render)
