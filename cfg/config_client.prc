# Default window properties...
window-title Panda
win-origin -1 -1
win-size 640 480
load-display pandagl
aux-display pandagl

model-cache-model #t
model-cache-textures #t
model-cache-compressed-textures 1
model-path .

# Performance...
hardware-animated-vertices #t
sync-video #f
smooth-lag 0.1
smooth-prediction-lag 0.0
basic-shaders-only #f
framebuffer-multisample 0
framebuffer-stencil 0
support-stencil 0
framebuffer-srgb 1
framebuffer-alpha 1
framebuffer-float 0
depth-bits 16
color-bits 16 16 16
alpha-bits 8
multisamples 0
garbage-collect-states-rate 0.5

preload-textures 1
preload-simple-textures 1
texture-compression 0
allow-incomplete-render 1
allow-async-bind 1
restore-initial-pose 0

textures-power-2 none
texture-minfilter mipmap
texture-magfilter linear
text-minfilter linear
text-magfilter linear
gl-coordinate-system default
gl-force-fbo-color 0
garbage-collect-states 0
allow-flatten-color 1
gl-debug 0
gl-finish 0
gl-debug-synchronous 1
gl-debug-abort-level fatal
gl-depth-zero-to-one 0
gl-force-depth-stencil 0
gl-compile-and-execute 1
glsl-preprocess 1
gl-version 3 2

text-flatten 1
text-dynamic-merge 1

interpolate-frames 1

# ========================================
# libpandabsp configurations

hdr-min-avg-lum 3.0
hdr-percent-bright-pixels 2.0
hdr-percent-target 60.0
hdr-debug-histogram #f
hdr-tonemap-scale 1.0

want-pssm 1
pssm-debug-cascades 0
pssm-splits 3
pssm-size 2048
pssm-shadow-depth-bias 0.0001
pssm-max-distance 200
pssm-sun-distance 400
pssm-normal-offset-scale 3.0
pssm-normal-offset-uv-space 1
pssm-softness-factor 2.0
pssm-cache-shaders 1
pssm-ambient-light-identifier 0.2 0.2 0.2
pssm-ambient-light-min 0.2 0.2 0.2
pssm-ambient-light-scale 15.0
shadow-depth-bits 32
stencil-bits 0

# Time averaged lighting in BSP levels to reduce popping
light-average 1
light-lerp-speed 5.0

mat_rimlight 1
mat_envmaps 1
mat_phong 1

r_ambientboost 1
r_ambientmin 0.3
r_ambientfraction 0.1
r_ambientfactor 5.0

r_bloomscale 1.0
r_bloomtintr 0.3
r_bloomtintg 0.59
r_bloomtintb 0.11
r_bloomtintexponent 2.2

decals_remove_overlapping 0
decals_max 30

# ========================================
