from src.bsp.BSPBase import BSPBase

class Game(BSPBase):

    def __init__(self):
        
        from panda3d.core import loadPrcFile
        loadPrcFile("cfg/config_client.prc")
        
        BSPBase.__init__(self)
        self.createShaderGenerator()
        self.createPostProcess()
        
        self.loadBSPLevel("mapsrc/example/example.bsp")
        
        base.enableMouse()
        base.camLens.setMinFov(70.0 / (4./3.))
        
base = Game()
base.run()
