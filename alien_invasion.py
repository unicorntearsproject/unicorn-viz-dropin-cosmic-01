"""
Alien Invasion — a descending saucer fleet over a churning nebula, each ship
throwing a real tractor beam down toward the ground, with a tasteful radar
sweep in the corner. Audio-reactive fleet glow, beam pulses, and starfield
sparkle.

Rebuilt from a flat two-circle-SDF "UFO" + a blown-out squared-glow hot spot
into detailed neon saucers (metal disc, glass dome, blinking rim lights) in
the same house style as Neon Pac's alien mode / Galaga's mystery ship, over a
proper animated nebula backdrop with twinkling stars and a distant skyline
silhouette the beams reach down toward.
"""
from __future__ import annotations

import moderngl

from unicornviz.effects.base import AudioData, BaseEffect

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
uniform float iHue;
uniform float iRadarX;
uniform float iRadarY;
uniform float iShipSpread;
uniform float iBeamSpread;
uniform int   iShipCount;
uniform int   iBeamCount;
in  vec2 v_uv;
out vec4 fragColor;

#define PI  3.14159265
#define TAU 6.28318530

float hash21(vec2 p) {
    p = fract(p * vec2(123.34, 456.21));
    p += dot(p, p + 45.32);
    return fract(p.x * p.y);
}
mat2 rot(float a) { float c = cos(a), s = sin(a); return mat2(c, -s, s, c); }
vec3 palette(float t) { return 0.5 + 0.5 * cos(TAU * (t + vec3(0.0, 0.33, 0.67))); }

// Churning nebula + twinkling stars + a faint city skyline at the horizon.
vec3 backdrop(vec2 uv, float t) {
    vec2 p = (uv - 0.5) * vec2(1.6, 1.0);
    float v = sin(p.x * 2.1 + t * 0.35) + sin(p.y * 1.7 - t * 0.28)
            + sin(length(p) * 2.6 - t * 0.5);
    vec3 col = palette(v * 0.09 + iHue + t * 0.015);
    col *= col;
    col *= 0.10 + 0.10 * (v * 0.5 + 0.5);

    float sh = hash21(floor(uv * vec2(140.0, 90.0)));
    if (sh > 0.965) {
        float tw = 0.5 + 0.5 * sin(t * (2.0 + sh * 6.0) + sh * 40.0);
        col += vec3(0.8, 0.85, 1.0) * tw * (0.35 + iTreble * 0.5);
    }

    float ground = smoothstep(0.16, 0.0, uv.y);
    float sky = hash21(floor(vec2(uv.x * 40.0, 0.0)));
    float bld = step(0.6, sky) * smoothstep(0.10 + sky * 0.05, 0.0, uv.y);
    col += vec3(0.05, 0.08, 0.16) * ground * 1.4;
    col += vec3(1.0, 0.75, 0.35) * bld * step(hash21(floor(vec2(uv.x * 40.0, 1.0))), 0.35) * 0.5;
    return col;
}

// A neon flying saucer in local space, q ~ roughly [-1,1], y up.
vec3 drawSaucer(vec2 q, vec3 tone, float t, float bob) {
    vec2 e = q;
    e.y -= bob;
    float disc = 1.0 - smoothstep(-0.03, 0.03, length(e / vec2(0.62, 0.16)) - 1.0);
    float dome = (1.0 - smoothstep(-0.03, 0.03,
                  length((e - vec2(0.0, 0.05)) / vec2(0.28, 0.30)) - 1.0)) * step(0.0, e.y);
    vec3 metal = mix(vec3(0.14, 0.20, 0.34), vec3(0.82, 0.90, 1.0),
                     clamp(e.y * 2.2 + 0.5, 0.0, 1.0));
    vec3 domecol = mix(tone, vec3(1.0), 0.35 + 0.25 * sin(t * 2.0));
    vec3 col = metal * disc;
    col = mix(col, domecol, dome * 0.85);
    col += vec3(1.0) * smoothstep(0.05, 0.0, length(e - vec2(-0.16, 0.10))) * dome * 0.7;  // spec
    for (int k = -3; k <= 3; k++) {                      // blinking rim lights
        vec3 lc = 0.5 + 0.5 * cos(vec3(0.0, 2.1, 4.2) + t * 6.0 + float(k) * 1.2);
        col += lc * smoothstep(0.020, 0.0, length(e - vec2(float(k) * 0.085, -0.02)))
             * disc * 0.9;
    }
    col += tone * smoothstep(1.1, 0.0, length(e)) * 0.10;  // soft aura, not a hot blob
    return col;
}

void main() {
    vec2 uv = v_uv;
    uv = (uv - 0.5) / max(iZoom, 0.01) + 0.5;
    float t = iTime;
    float fleet_glow = 0.55 + iBass * 0.55 + iMid * 0.25;

    vec3 col = backdrop(uv, t);

    for (int i = 0; i < 8; i++) {
        if (i >= iShipCount) break;
        float fi = float(i);
        float seed = fi * 0.37;
        float angle = seed * 1.9 + iVariant * 4.0;
        vec2 orbit = vec2(cos(angle), sin(angle * 1.3) * 0.35) * (0.16 + iShipSpread * 0.20);
        vec2 drift = vec2(
            sin(t * (0.22 + iVariant * 0.10) + seed * 1.1) * (0.10 + iShipSpread * 0.05),
            (fract(t * (0.035 + iVariant * 0.012) + seed) - 0.5) * (0.62 + iShipSpread * 0.10)
        );
        vec2 centre = vec2(0.5, 0.62) + orbit + drift;
        vec2 q = (uv - centre) / vec2(0.11, 0.11 * 1.6);
        float bob = sin(t * (1.6 + seed) ) * 0.06;
        vec3 tone = mix(vec3(0.2, 0.9, 1.0), palette(0.4 + iHue + seed * 0.2), 0.55);

        // Tractor beam down to the ground from this ship's belly.
        float top = centre.y - 0.02;
        if (i < iBeamCount) {
            float bw = mix(0.012, 0.11, clamp((top - uv.y) / max(top + 0.9, 1e-3), 0.0, 1.0));
            bw *= (0.6 + iBeamSpread * 2.2);
            float inBeam = smoothstep(bw, 0.0, abs(uv.x - centre.x)) * step(uv.y, top);
            float motes = hash21(floor(vec2(uv.x * 60.0, uv.y * 14.0 - t * 3.0)));
            float sparkle = step(0.965, motes) * (0.4 + iTreble * 0.8);
            vec3 beamCol = mix(vec3(0.25, 1.0, 0.55), tone, 0.4);
            col += beamCol * inBeam * (0.10 + iBass * 0.16 + 0.05 * sin(t * 3.0 + seed * 5.0));
            col += beamCol * sparkle * inBeam * 0.5;
        }

        col += drawSaucer(q, tone, t + seed * 3.0, bob * 4.0) * fleet_glow;
    }

    // Tasteful radar sweep, tucked in a corner, well below fleet brightness.
    vec2 radarC = vec2(iRadarX, iRadarY);
    float rr = length(uv - radarC);
    float ang = atan(uv.y - radarC.y, uv.x - radarC.x);
    float sweep = fract(t * 0.16 - ang / TAU);
    float ring = smoothstep(0.11, 0.0, abs(rr - 0.09)) * smoothstep(0.10, 0.0, rr);
    float fade = smoothstep(0.55, 0.0, sweep);
    col += vec3(0.25, 1.0, 0.5) * ring * fade * 0.35;
    col += vec3(0.15, 0.7, 0.3) * smoothstep(0.09, 0.0, rr) * 0.05;

    float vig = smoothstep(1.25, 0.25, length(uv - 0.5));
    col *= vig;
    col = col / (1.0 + col * 0.5);
    col = pow(clamp(col, 0.0, 1.0), vec3(0.85));
    fragColor = vec4(col, 1.0);
}
"""


class AlienInvasion(BaseEffect):
    """Descending neon UFO fleet with real tractor beams over a nebula."""

    NAME = "Alien Invasion"
    AUTHOR = "unicorn-viz"
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
        self._hue = float(self.rng.uniform(0.0, 1.0))
        self.parameters = {
            "fleet_speed": float(self.config.get("fleet_speed", 1.2)),
            "beam_intensity": float(self.config.get("beam_intensity", 1.0)),
            "radar_sweep": float(self.config.get("radar_sweep", 0.8)),
            'zoom': float(self.config.get('zoom', self.rng.uniform(0.82, 1.12))),
        }
        self._prog = self._make_program(_VERT, _FRAG)
        self._vao, self._vbo = self._fullscreen_quad(self._prog)
        self._radar_x = float(self.rng.uniform(0.12, 0.28))
        self._radar_y = float(self.rng.uniform(0.74, 0.88))
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
        self._prog["iHue"].value = self._hue
        self._prog["iRadarX"].value = self._radar_x
        self._prog["iRadarY"].value = self._radar_y
        self._prog["iShipSpread"].value = self._ship_spread
        self._prog["iBeamSpread"].value = self._beam_spread * self.parameters["beam_intensity"]
        self._prog["iShipCount"].value = self._ship_count
        self._prog["iBeamCount"].value = self._beam_count
        self._vao.render(moderngl.TRIANGLE_STRIP)

    def destroy(self) -> None:
        self._vao.release()
        self._vbo.release()
        self._prog.release()
