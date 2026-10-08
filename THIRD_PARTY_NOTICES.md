# Sources and attribution

Original Imaging Recipes belong to their credited creators. Source archive: [shouryan01/Nikon-Recipes](https://github.com/shouryan01/Nikon-Recipes); upstream NP3 files are linked, not redistributed here. Archive availability is not treated as permission to relicense the creators' originals.

Adobe RGBTable layout and tetrahedral behavior were investigated against the [Adobe DNG SDK reference mirror](https://android.googlesource.com/platform/external/dng_sdk/+/de700ad461e35af50b28b861943a0b0753b10929/source/dng_reference.cpp). This repository contains Python format/math implementations, not the Adobe SDK source, binaries or base profiles. The public RGBTable codec was implemented afresh from the observed stream layout; an ambiguously attributed exploratory encoder was not copied into this repository.

CIEDE2000 reference examples: [Sharma, Wu and Dalal's supplementary data](https://hajim.rochester.edu/ece/sites/gsharma/ciede2000/). NumPy, SciPy, tifffile and Pillow are external dependencies under their respective upstream licenses, not relicensed as project code. Nikon, Lightroom and Adobe Camera Raw are their owners' trademarks.

The software is independent and does not imply Nikon/Adobe endorsement. Photo rights are governed by `samples/LICENSE.md`, not MIT.
