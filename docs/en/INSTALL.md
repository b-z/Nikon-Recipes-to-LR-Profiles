# Install 0.2.0 profiles

1. Unzip this archive. In Lightroom / Camera Raw, open the Profile Browser and select Import Profiles. Choose the `.xmp` files in `profiles/`. No separate DCP or installer is needed.
2. Restart Lightroom if the imported profiles do not appear. Open **Nikon Recipes LR 0.2** and choose a style.
3. Adjust Amount (0–200%); try 30–50% for subtle application. Continue editing exposure, white balance and other settings as usual.

All 236 Nikon conversions use **Y8**: a smooth spline fit sampled to a 32³ RGB table, which trades some chart accuracy for smoother gradients. The 58 recipes that still showed banding with the previous Y7 tables were checked by the maintainer with Y8 on several real photographs, and no banding was observed. The other 178 were not individually reviewed with Y8. Banding remains a known risk, especially in smooth sky and bokeh gradients and at high Amount. Only Nikon Z8 has been tested.

0.2.0 profiles have new names, a new group and new UUIDs, so they can be installed next to 0.1 profiles. Remove the **Nikon Recipes LR 0.1** profiles if you no longer need them.

Recipe authors are credited in each profile and `manifest.json`. Original NP3 files are external inputs from https://github.com/shouryan01/Nikon-Recipes or their creators. Tool code and project-created conversion resources follow the included MIT license and PROFILE_LICENSE notice. Sample photos follow separate terms and are not included in this profile pack.

Scores and comparisons: https://github.com/b-z/Nikon-Recipes-to-LR-Profiles . The release does not include Fuji film simulation conversions.
