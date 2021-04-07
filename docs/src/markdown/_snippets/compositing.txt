<style>
img {
  background: white;
}

.circle {
  display: block;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  position: absolute;
  transition: all 0.5s ease;
  z-index: 10;
}

.isolate label {
    position: absolute;
    bottom: 0;
    width: 100%;
    text-align: center;
}

.circle-1 {
  background: #f5d311;
}

.dual .circle-1 {
  background: #fc3d99;
}

.isolate:not(.dual):hover .circle-1 {
  transform: translateX(-10px) translateY(-7.5px);
}

.isolate.dual:hover .circle-1 {
  transform: translateX(-10px);
}

.circle-2 {
  background: #fc3d99;
  left: 40px;
}

.dual .circle-2 {
  background: #07c7ed;
}

.isolate:not(.dual):hover .circle-2 {
  transform: translateX(10px) translateY(-7.5px);
}

.isolate.dual:hover .circle-2 {
  transform: translateX(20px);
}

.circle-3 {
  background: #07c7ed;
  left: 20px;
  top: 40px;
}

.isolate:not(.dual):hover .circle-3 {
  transform: translateY(7.5px);
}

.isolate {
  display: block;
  height: 120px;
  width:  120px;
  isolation: isolate;
  position: relative;
  margin: 0 10px;
}

.isolate.dual {
  height: 80px;
}

div.blend-wrap {
  display: flex;
  min-height: calc(120px + 0.8em);
  width: 100%;
}

div.blend-wrap > :not(.blend-content) {
  order: 0;
}

div.blend-wrap .isolate {
  margin-top:  0.8em;
}

div.blend-wrap > .blend-content {
  order: 1;
}

.blend-normal .circle {
  mix-blend-mode: normal;
}

.blend-multiply .circle {
  mix-blend-mode: multiply;
}

.blend-screen .circle {
  mix-blend-mode: screen;
}

.blend-overlay .circle {
  mix-blend-mode: overlay;
}

.blend-color-burn .circle {
  mix-blend-mode: color-burn;
}

.blend-color-dodge .circle {
  mix-blend-mode: color-dodge;
}

.blend-exclusion .circle {
  mix-blend-mode: exclusion;
}

.blend-difference .circle {
  mix-blend-mode: difference;
}

.blend-darken .circle {
  mix-blend-mode: darken;
}

.blend-lighten .circle {
  mix-blend-mode: lighten;
}

.blend-soft-light .circle {
  mix-blend-mode: soft-light;
}

.blend-hard-light .circle {
  mix-blend-mode: hard-light;
}

.blend-hue .circle {
  mix-blend-mode: hue;
}

.blend-saturation .circle {
  mix-blend-mode: saturation;
}

.blend-luminosity .circle {
  mix-blend-mode: luminosity;
}

.blend-color .circle {
  mix-blend-mode: color;
}
</style>
