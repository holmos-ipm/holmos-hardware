# Shopping List

Links to shops with low-cost components tend to not last very long.
Often, the exact same items are available from different distributors, so try a search engine.
If you find something that works, please consider updating/adding a link here.

## Electronics
The links are pretty stable, but you might be able to find cheaper sources.

* Raspberry Pi 3B+ [35€ 3B+, RS](https://de.rs-online.com/web/p/entwicklungskits-prozessor-mikrocontroller/1373331/)
* RPi Camera v2 noIR [25€ RS](https://de.rs-online.com/web/p/videomodule/9132673/)
* SD card for the operating system

The code should work on other RPis as well.

Using a different camera is more complicated. 
If the pixel pitch is the same (2 * 1.12 µm from one red pixel to the next), you only™ need to change the code to use your camera.
To use a camera with different pixel pitch, read and understand the [optics design](instructions/optics_design.md).
You'll need to adjust the hardware as well.

## Mechanics
* 3D-Print (PLA) less than 10€ material costs.
* M3x10 7 pcs, 3 Nuts
  * 4 pcs for RPi (M3 pretty tight in some boards...)
  * 3 pcs and nuts for round mounts
* M2.5x4 4 pcs for the camera mount
* Steel rods 3Stk, 6mm*1m [15€ Hornbach](https://www.hornbach.de/shop/Rundstange-Edelstahl-6-mm-1-m/7813904/artikel.html)


## Optics
### Objective
The reference design uses a 4x objective lens from 
[55 € edmund optics](https://www.edmundoptics.de/p/4x-din-achromatic-commercial-grade-objective/5381/)

There are cheaper sources (sometimes with very similar quality), but using lower quality here can really hurt.
You can use different lenses by changing the diameter of the mount.
Keep in mind that the reference beam passes close to the objective: objectives with larger housings will block the beam.

### Condensor lens
An f=100 mm, d=25.4 mm lens is in the reference design, but similar lenses work with changes to the distances.
Adjust the mount diameter to fit your lens.
Using less than ~ 10 mm diameter will degrade the optical quality of you microscope.
  * There is a great lens, a real glass achromat, that is available in different webshops, usually specified as f~=99, d=26, e.g. [here 4,90€](hhttps://pgi-shop.de/achromat-linse-oe-26-0-mm-f-99-6-mm/)
  * Polymer lenses work, too.
  * (f=80mm, d=20mm [25€ edmund](https://www.edmundoptics.com/p/200mm-dia-x-800mm-fl-uncoated-plano-convex-lens/5903/))
  
### Beamsplitter: 
A "Teildurchlässiger Vorderflächen-Glasspiegel, 30 x 40 mm" keeps popping up in educational shops, e.g. 
[here 6,90€](https://pgi-shop.de/teildurchlaessiger-vorderflaechen-glasspiegel-30-x-40-mm/).

40 mm width is needed for the clip. 
These flat metal-on-glass beamsplitters work very well, and 50:50 is perfectly fine.
The front (i.e. coated) side faces the laser.

### Mirror
Use a front surface mirror for the reference beam. 
A "Vorderflächen-Glasspiegel, 22,0 x 15,5 mm" is usually available in german webshops, e.g.
[2,90 € here](https://pgi-shop.de/vorderflaechen-glasspiegel-22-0-x-15-5-mm/)

### Laser
We have used dd635-1-512x342 or DOE-QD650-0.4-12-10-22 from [Laserfuchs](https://www.laserfuchs.de]) (Their links go out of date quickly, though...).
 * It needs to be uncollimated, emitting a divergent beam:
    * Very cheap lasers come with glued-on lens. These can be removed with force/axes/saws/..., but you risk damaging the laser.
    * Some moderately cheap lasers (see above) come with a screw-in lens that can be removed easily.
 * No need for power, you are shining straight into the camera. Do your eyes a favor and use a Class 1 Laser.
 * Small laser modules with 5V input can be powered from a RPi USB port 
 * Adjust the mount diameter to fit your laser.
