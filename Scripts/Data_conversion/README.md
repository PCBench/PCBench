# Data conversion

## Convert KiCAD 6&7 files to KiCAD 5

Identify the KiCAD6 PCB files with:

```
ls ../../PCBs/**/raw.kicad_pro
```

The files are already moved to ../../PCBs_KiCAD6 folder.

Now run the convertion script:

```
python3 kicad6to5.py
```

The script will convert `../../PCBs_KiCAD6` projects into kicad 5 format `export5.kicad_pcb`:

```sh
ls ../../PCBs_KiCAD6/kitspace_beehive
# export5.kicad_pcb    -> generated kicad 5 file
# metadata.json
# raw.kicad_pcb        -> kicad 6 file
# raw.kicad_pro
```

The generated files are included.
