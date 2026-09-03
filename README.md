# cosmic-01 — Unicorn Viz effect pack

**Version 0.11.2**


deep space / lensing / trippy cosmic visuals

## Changelog

- **0.11.2** — Alien Invasion: the starfield's stars were a bare threshold on a
  cell hash, which fills the whole square cell and reads as a grid of hard
  little marks. Each star is now a soft round point placed inside its cell.

- **0.11.1** — fixed a crash-on-load bug in Sun Ship 3000: `iTreble` was
  declared and set from Python but never referenced in the compiled
  fragment shader, so moderngl's uniform map didn't contain it and the
  very first `render()` call raised `KeyError`. This was found via a
  live crash report, then a codebase-wide static sweep for the same
  bug class (a uniform assigned from Python but stripped by the GLSL
  compiler for being unused) turned up no other instances. Wired
  `iTreble` into the laser/spark density the effect's own docstring
  already promised: enemy and player laser-fire brightness and the
  enemy spark-bloom glint now scale with treble, instead of the
  uniform sitting dead. Verified with a real moderngl render across
  quiet/moderate/loud-beat audio, a high-iTime stress test, and a
  direct treble-on-vs-off brightness comparison.
- **0.11.0** — float32 time/audio pass (2026-08-03 audit §8): Sun Ship 3000 CPU-integrates its mid/treble/explosion phases (formation, fleet hue, and fire accelerate with the music instead of strobing to random positions each frame); Alien Invasion beam motes and Cosmos starfield/nebula wrap their time terms before hashing (motes no longer freeze into stripes; stars no longer band).
- **0.10.0** — Alien Invasion rebuilt: flat two-circle-SDF "UFOs" replaced
  with detailed neon saucers (metal disc, glass dome, blinking rim lights) in
  the house style shared with Neon Pac / Galaga; the static full-height light
  columns replaced with real tapering tractor beams reaching toward the
  ground; added a churning nebula backdrop, twinkling stars, and a distant
  skyline glow. Removed the blown-out squared-glow hot-core term that made
  each ship read as an overly bright moving spot; ships now use soft, capped
  glow instead. The radar sweep is now tucked low-key in a corner instead of
  competing for brightness.
- **0.9.0** — initial versioned release.
