# potree_kickstarter
Kickstarts potree with colored dutch elevation pointcloud.

Provides python script which:
    * Downloads part of the dutch elevation model (AHN2 kaartblad)
    * Merges filtered and unfiltered pointcloud
    * Colors pointcloud by WMS/WCS
    * Runs PoTreeConverter on colored pointcloud

Depends on the following external tools (in Path):
    * GDAL
    * Laslib (laz compression enabled)
    * PoTreeConverter
    
An ansible script for compiling these dependencies in Ubuntu 15.10 is provided.

