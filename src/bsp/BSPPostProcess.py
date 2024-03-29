from panda3d.core import Shader, PTA_LVecBase3f, Vec3
from panda3d.bsp import PostProcess, PostProcessPass, PostProcessEffect, bits_PASSTEXTURE_COLOR, HDREffect, BloomEffect

class BSPPostProcess(PostProcess):
    
    def __init__(self):
        PostProcess.__init__(self, base.win)
        
        self.hdr = None
        self.bloom = None
        
        self.flashEnabled = True
        self.flashColor = PTA_LVecBase3f.emptyArray(1)
        self.setFlashColor(Vec3(0))
        
    def enableFlash(self, color = Vec3(0)):
        self.flashEnabled = True
        self.setFlashColor(color)
        
    def setFlashColor(self, color):
        self.flashColor.setElement(0, color)
        
    def disableFlash(self):
        self.flashEnabled = False
        self.setFlashColor(Vec3(0))
        
    def cleanup(self):
        if self.hdr:
            self.hdr.shutdown()
            self.removeEffect(self.hdr)
        self.hdr = None
        
        if self.bloom:
            self.bloom.shutdown()
            self.removeEffect(self.bloom)
        self.bloom = None
        
    def setup(self, bloom = True, hdr = True):
        self.cleanup()
        
        textures = {"sceneColorSampler": self.getSceneColorTexture()}
        
        if hdr:
            self.hdr = HDREffect(self)
            self.hdr.getHdrPass().setExposureOutput(base.shaderGenerator.getExposureAdjustment())
            self.addEffect(self.hdr)
        
        if bloom:
            self.bloom = BloomEffect(self)
            self.addEffect(self.bloom)
            textures["bloomSampler"] = self.bloom.getFinalTexture()
        
        finalQuad = self.getScenePass().getQuad()
        
        vtext = "#version 330\n"
        vtext += "uniform mat4 p3d_ModelViewProjectionMatrix;\n"
        vtext += "in vec4 p3d_Vertex;\n"
        vtext += "in vec4 texcoord;\n"
        vtext += "out vec2 l_texcoord;\n"
        vtext += "void main()\n"
        vtext += "{\n"
        vtext += "  gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;\n"
        vtext += "  l_texcoord = texcoord.xy;\n"
        vtext += "}\n"

        ptext = "#version 330\n"
        ptext += "out vec4 outputColor;\n"
        ptext += "in vec2 l_texcoord;\n"

        for sampler in textures.keys():
            ptext += "uniform sampler2D " + sampler + ";\n"
            
        if self.flashEnabled:
            ptext += "uniform vec3 flashColor[1];\n"

        ptext += "void main()\n"
        ptext += "{\n"
        ptext += "  outputColor = texture(sceneColorSampler, l_texcoord);\n"
        if bloom:
            ptext += "  outputColor.rgb += texture(bloomSampler, l_texcoord).rgb;\n"
        if self.flashEnabled:
            ptext += "  outputColor.rgb += pow(flashColor[0], vec3(2.2));\n"
        ptext += "}\n"

        shader = Shader.make(Shader.SL_GLSL, vtext, ptext)
        if not shader:
            return
            
        finalQuad.setShader(shader)
        
        for sampler, texture in textures.items():
            finalQuad.setShaderInput(sampler, texture)
            
        if self.flashEnabled:
            finalQuad.setShaderInput("flashColor", self.flashColor)
