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

# Requirements
   * [Ubuntu 15.10 machine](http://www.ubuntu.com/download/desktop)
   * [Python 2.7.5](https://www.python.org/downloads/)
   * pip `apt-get install python-pip`
   * python markupsafe `pip install markupsafe`
   * python ansible `pip install ansible`
   * Lastools, laszip and liblas. To download, compile and install those correctly an ansible script is available in another git [porject](https://github.com/openearth/stack). Download this stack and in the stack directory run the following command to start this ansible playbook: `ansible-playbook -i hosts playbook.yml -l lastools -t lastools -K -vvv"


