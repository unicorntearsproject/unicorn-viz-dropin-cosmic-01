"""
Alien Invasion — UFO fleets descending from above, atmospheric probing beams,
and planetary radar scan overlays. Audio-reactive fleet intensity and beam pulses.
"""
from __future__ import annotations

import math
import numpy as np
import moderngl

from unicornviz.effects.base import BaseEffect, AudioData

_VERT = """
#version 330
in vec2 in_vert;
out vec2 v_uv;
void main() {
    v_uv = in_vert * 0.5 + 0.5;
    gl_Position = vec4(in_vert, 0.0, 1.0);
}
"""

_FRAG = """
#version 330
uniform float iTime;
uniform float iBass;
uniform float iMid;
uniform float iTreble;
uniform float iZoom;
uniform float iVariant;
uniform float iRadarX;
uniform float iRadarY;
uniform float iShipSpread;
uniform float iBeamSpread;
uniform int iShipCount;
uniform int iBeamCount;
in vec2 v_uv;
out vec4 fragColor;

vec3 palette(float t) {
    vec3 a = vec3(0.5, 0.5, 0.5);
    vec3 b = vec3(0.5, 0.5, 0.5);
    vec3 c = vec3(1.0, 1.0, 1.0);
    vec3 d = vec3(0.02, 0.23, 0.45);
    return a + b * cos(6.28318 * (c * t + d));
}

// Alien ship SDF
float ufo(vec2 p, float seed) {
    p.y += sin(iTime * (1.7 + iVariant * 0.55) + seed * 1.7) * (0.22 + iVariant * 0.08);
    float body = length(p - vec2(0.0, 0.0)) - 0.15;
    float dome = length(p - vec2(0.0, -0.08)) - 0.08;
    return min(body, dome);
}

// Probing beam
float beam(vec2 p, float time) {
    float beam_width = 0.04 + sin(time * (4.0 + iVariant)) * 0.018;
    float dist = abs(p.x - 0.5);
    float height = 1.0 - p.y;
    return smoothstep(beam_width, 0.0, dist) * height;
}

// Planetary radar scan
float radar_scan(vec2 p, float time) {
    vec2 radar_center = vec2(iRadarX, iRadarY);
    float r = length(p - radar_center);
    float angle = atan(p.y - radar_center.y, p.x - radar_center.x);
    float sweep = fract((time * 0.5 + angle / 6.28) * 2.0);
    return smoothstep(0.15, 0.0, abs(r - 0.2 - sweep * 0.1)) * 0.6;
}

void main() {
    vec2 uv = v_uv;
    uv = (uv - 0.5) / max(iZoom, 0.01) + 0.5;
    float hue_shift = iTime * (0.05 + iVariant * 0.02);
    vec3 col = mix(vec3(0.008, 0.015, 0.03), palette(0.1 + hue_shift + iVariant * 0.2) * 0.09, 0.45);
    
    // Star field
    float stars = sin(uv.x * (92.0 + iVariant * 18.0)) * sin(uv.y * (104.0 + iVariant * 22.0));
    col += vec3(1.0, 0.98, 0.9) * max(0.0, stars - 0.985) * (2.6 + iVariant * 0.5);
    
    // Fleet of UFOs in formation
    float fleet_intensity = 0.45 + iBass * 0.85 + iMid * 0.5;
    for (int i = 0; i < 8; i++) {
        if (i >= iShipCount) {
            break;
        }
        float seed = float(i) * 0.3;
        float angle = seed * 1.9 + iVariant * 4.0;
        vec2 orbit = vec2(cos(angle), sin(angle * 1.3)) * (0.18 + iShipSpread * 0.22);
        vec2 motion = vec2(
            sin(iTime * (0.85 + iVariant * 0.28) + seed * 1.1),
            cos(iTime * (1.05 + iVariant * 0.22) + seed * 0.9)
        ) * (0.14 + iShipSpread * 0.08);
        vec2 ufo_pos = uv + orbit + motion;
        float d = ufo(ufo_pos, seed);
        float glow = exp(-d * d * 20.0);
        vec3 fleet_col = mix(vec3(0.18, 0.86, 1.0), palette(0.35 + hue_shift + seed * 0.22 + iVariant * 0.1), 0.58);
        col += fleet_col * glow * fleet_intensity * (0.42 + iShipSpread * 0.18);
        col += vec3(1.0, 0.95, 0.8) * glow * glow * (0.12 + iShipSpread * 0.05);
    }
    
    // Probing beams (multiple beams)
    float beam_sum = 0.0;
    for (int i = 0; i < 5; i++) {
        if (i >= iBeamCount) {
            break;
        }
        float beam_offset = (float(i) - float(iBeamCount - 1) * 0.5) * iBeamSpread;
        vec2 beam_uv = uv + vec2(beam_offset, 0.0);
        beam_sum += beam(beam_uv, iTime + float(i) * 1.57 + iVariant * 2.0);
    }
    vec3 beam_col = mix(vec3(0.0, 1.0, 0.6), palette(0.62 + hue_shift + iVariant * 0.15), 0.45);
    col += beam_col * beam_sum * (iTreble * 0.9 + 0.38);
    
    // Radar scan overlay
    vec3 radar_col = mix(vec3(0.2, 1.0, 0.4), palette(0.8 + hue_shift + iVariant * 0.25), 0.45);
    col += radar_col * radar_scan(uv, iTime);
    
    // Atmospheric distortion
    float distort = sin(uv.y * (28.0 + iVariant * 5.0) + iTime * (2.7 + iVariant * 0.4)) * 0.02;
    col += vec3(0.1, 0.2, 0.3) * abs(distort) * (iMid + 0.15);
    
    // Pulse/alarm effect on beat
    float pulse = smoothstep(0.5, 0.0, fract(iTime * (3.5 + iVariant * 0.8) + iTreble * 2.0));
    col += mix(vec3(1.0, 0.2, 0.2), palette(0.95 + hue_shift + iVariant * 0.25), 0.35) * pulse * 0.16;
    col += vec3(0.08, 0.12, 0.18) * iMid * (0.35 + iVariant * 0.2);
    
    fragColor = vec4(col, 1.0);
}
"""

class AlienInvasion(BaseEffect):
    NAME = "Alien Invasion"
    AUTHOR = "Autopilot"
    TAGS = ['cosmic', 'sci-fi', 'procedural', 'groovy']
    PING_PONG_FRIENDS = [
        'Cosmos',
        'Copper Bars',
        'Hexy Stars',
        'Metaballs',
        'Plasma',
        'Wormhole',
        'Psychedelic',
        'Van Gogh',
        'Wavey Gravy',
        'Tron Grid',
        'Kaleidoscope',
        'Unicorn Tears',
    ]

    def _init(self) -> None:
        self._variant = float(self.rng.uniform(0.0, 1.0))
        self.parameters = {
            "fleet_speed": float(self.config.get("fleet_speed", 1.2)),
            "beam_intensity": float(self.config.get("beam_intensity", 1.0)),
            "radar_sweep": float(self.config.get("radar_sweep", 0.8)),
            'zoom': float(self.config.get('zoom', self.rng.uniform(0.82, 1.12))),
        }
        self._prog = self._make_program(_VERT, _FRAG)
        self._vao, self._vbo = self._fullscreen_quad(self._prog)
        self._radar_x = float(self.rng.uniform(0.35, 0.65))
        self._radar_y = float(self.rng.uniform(0.20, 0.42))
        self._ship_spread = float(self.rng.uniform(0.78, 1.35))
        self._beam_spread = float(self.rng.uniform(0.12, 0.24))
        self._ship_count = int(self.rng.integers(4, 9))
        self._beam_count = int(self.rng.integers(2, 6))
        self._bass = 0.0
        self._mid = 0.0
        self._treble = 0.0

    def update(self, dt: float, audio: AudioData) -> None:
        super().update(dt, audio)
        self._bass = audio.bass_n
        self._mid = audio.mid_n
        self._treble = audio.treble_n

    def render(self) -> None:
        self._prog["iTime"].value = self.time * self.parameters["fleet_speed"]
        self._prog["iBass"].value = self._bass
        self._prog["iMid"].value = self._mid
        self._prog["iTreble"].value = self._treble
        self._prog["iZoom"].value = float(self.parameters['zoom'])
        self._prog["iVariant"].value = self._variant
        self._prog["iRadarX"].value = self._radar_x
        self._prog["iRadarY"].value = self._radar_y
        self._prog["iShipSpread"].value = self._ship_spread
        self._prog["iBeamSpread"].value = self._beam_spread
        self._prog["iShipCount"].value = self._ship_count
        self._prog["iBeamCount"].value = self._beam_count
        self._vao.render(moderngl.TRIANGLE_STRIP)

    def destroy(self) -> None:
        self._vao.release()
        self._vbo.release()
        self._prog.release()
