# Analysis Template

Author: Yige Huang

Date: 03.03.2024

Version: 2.1

## Quick start

This template is a simple example of using CMake to build executable with `AnalysisTree` and some other modules (like `IdxConstants`, `MultiplicityTool`, `CbmCut` and `DuplicateRemover`).

1. Modify `src/AnalysisTemplate.cpp`

2. Put necessary modules into `src`, e.g. `src/IdxConstants`

3. Add additional `add_libraries(MODULE_NAME MODULE_SRC)` into `CMakeFileLists.txt`

4. Run `./install.sh`

5. If you want to clean the folder, run `./install.sh uninstall`

## Patch Note

* 03.03.2024 by yghuang v2.1:

> Add `CbmCut` module
>
> Minor change to `IdxConstants`

* 28.02.2024 by yghuang v2.0:

> Example with 3 modules.

* 21.02.2024 by yghuang v1.0:

> First version.
