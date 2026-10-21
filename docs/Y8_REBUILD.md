# Y8 smooth-function rebuild

All 236 Nikon recipes have separate Y8 downloads and four-scene previews. Y7 and NX references remain available. Fuji simulations are excluded.

## What changed

Y7 optimized the 32³ table directly with a global slope-jump penalty. Y8 instead fits a bounded C2 continuous cubic tensor spline with 16 control points per axis, penalizes curvature, then samples that function into the delivered32³ table. This reduces fitting freedom from 32768 to 4096 coefficients per output channel and discourages local compression/expansion waves between chart samples. It does not increase LUT density or change Adobe interpolation.

## Real-photo review

The maintainer reviewed the 58 recipes previously flagged for residual Y7 banding on multiple real photographs and reported good results with no banding observed. The other178 recipes have not received that same review. This does not establish a universal no-banding guarantee. Historical warning icons refer to Y7.

## Tradeoff and validation

Fits use the same existing NX chart targets and train/validation/test color-group split. Some recipes sacrifice chart color accuracy for smoothness; Y8 is not uniformly more accurate. In the four-recipe controlled experiment, Vintage Touch's heldout mean ΔE increased 0.477→0.608, while actual Camera Raw sky slope ripple fell about 84%. Its independent 32-panel gradient L-ripple p95 fell about 12%. Those percentages are diagnostic metric reductions, not percentages of visible bands removed.

All 236 XMPs converged, decoded exactly, and have distinct UUIDs. Every displayed Y8 conversion is a numerical native tetrahedral preview on the same Camera Raw Adobe Standard baseline used for Y7, color-managed to sRGB. They are not 944 new Camera Raw exports or NX truth. NX images are the original maintainer-exported references. Vintage Touch Y7/Y8 was checked by actual Camera Raw; geometry correction was disabled on a private copy without changing RAW data. The gallery's baselines preserve the existing matched geometry.

Chart ΔE uses the same valid-sample policy as Y7. Banding risk is global native face-jump p99, not a perceptual pass/fail threshold.

## Per-recipe scores

| Recipe | Y7 chart ΔE | Y8 chart ΔE | Y8 banding risk |
|---|---:|---:|---:|
| 24Look (24Look_24Frames) | 0.615 | 0.927 | 0.593 |
| A-X+rossandhisjpegs (A-X+rossandhisjpegs) | 0.349 | 0.148 | 0.436 |
| AgU100 (AgU100) | 0.408 | 0.630 | 0.476 |
| Air Green (AirGreen_Gunji) | 0.873 | 1.413 | 0.884 |
| ArmitageEktar100 (ArmitageEktar100) | 0.414 | 0.579 | 0.424 |
| ArmitageKGold200 (ArmitageKGold200) | 0.366 | 0.547 | 0.352 |
| ArmitageKPortra800 (ArmitageKPortra800) | 0.535 | 0.779 | 0.538 |
| ArmitageProvia100F (ArmitageProvia100F) | 0.473 | 0.743 | 0.535 |
| ArmitageWarmAutumn (ArmitageWarmAutumn) | 0.494 | 0.889 | 0.417 |
| At Dusk (At_Dusk_Woo) | 0.500 | 0.753 | 0.537 |
| B-7+rossandhisjpegs (B-7+rossandhisjpegs) | 0.573 | 0.890 | 0.547 |
| Bleach Blue (BleachBlue_Aparupa) | 0.630 | 0.829 | 0.472 |
| Bleach Bypass 01a (BleachBypass_01a) | 0.268 | 0.306 | 0.292 |
| Blue Hour (BlueHour_Luna) | 0.371 | 0.556 | 0.434 |
| BlueM (BlueM_LUIZCLAS) | 0.574 | 0.803 | 0.398 |
| Bluegrain (Bluegrain_jyota) | 0.370 | 0.574 | 0.442 |
| Boho Look (BohoLook_EmilieH) | 0.379 | 0.607 | 0.592 |
| BritFilmBW (BritFilmBW_Vincent) | 0.405 | 0.254 | 0.290 |
| CINENigRed (CINENigRed_Fuji) | 0.527 | 0.820 | 0.426 |
| CRYSClear (CRYSClear_Eisuke) | 0.525 | 0.750 | 0.547 |
| CUBANO (CUBANO) | 0.670 | 0.985 | 0.513 |
| CafeCat (CafeCat_yw) | 0.292 | 0.388 | 0.304 |
| Call It Love (CallItLove_Faloo_Mi) | 0.490 | 0.731 | 0.400 |
| Calm Breeze (CalmBreeze_Dondre) | 0.341 | 0.495 | 0.431 |
| Catgrain (Catgrain_yw) | 0.292 | 0.388 | 0.304 |
| CineAchromic (CineAchromic) | 0.303 | 0.124 | 0.248 |
| CineBias (CineBias-BB) | 0.266 | 0.329 | 0.318 |
| CineBias (CineBias-C) | 0.403 | 0.565 | 0.398 |
| CineBias (CineBias-CC) | 0.389 | 0.553 | 0.364 |
| CineBias (CineBias-T) | 0.364 | 0.486 | 0.311 |
| CineBias (CineBias-TC) | 0.342 | 0.456 | 0.354 |
| CineBias (CineBias-WC) | 0.389 | 0.553 | 0.364 |
| CineBiasOffset (CineBiasOffset) | 0.338 | 0.486 | 0.322 |
| CineBias (CineBias_RED) | 0.292 | 0.388 | 0.304 |
| CineBlue (CineBlue_BrandonW) | 0.606 | 0.883 | 0.499 |
| CineM (CineM_LUIZCLAS) | 0.382 | 0.486 | 0.352 |
| Classic Chrome (Classic_Chrome) | 0.439 | 0.606 | 0.352 |
| Cloudy Forest (CloudyForest_Y2) | 0.354 | 0.523 | 0.394 |
| ClrMode Bu 01a (ClrMode_Bu_01a) | 0.494 | 0.771 | 0.361 |
| ClrMode Bu 01b (ClrMode_Bu_01b) | 0.578 | 0.877 | 0.373 |
| ClrMode Gn 01a (ClrMode_Gn_01a) | 0.457 | 0.716 | 0.485 |
| ClrMode Gn 01b (ClrMode_Gn_01b) | 0.491 | 0.791 | 0.483 |
| ClrMode TealOr 01a (ClrMode_TealOr_01a) | 0.609 | 0.862 | 0.480 |
| ClrMode TealOr 01b (ClrMode_TealOr_01b) | 0.877 | 1.221 | 0.499 |
| ClrMode Ye 01a (ClrMode_Ye_01a) | 0.405 | 0.628 | 0.462 |
| ClrMode Ye 01b (ClrMode_Ye_01b) | 0.519 | 0.771 | 0.455 |
| ClrPortrait (ClrPortrait_TSakai) | 0.329 | 0.516 | 0.374 |
| Coastal Glow (Coastal_Glow_NM) | 0.587 | 0.903 | 0.568 |
| Color Splash (ColorSplash_Gilmar) | 0.448 | 0.649 | 0.473 |
| Cozy Autumn (CozyAutumn_Leno) | 0.300 | 0.394 | 0.310 |
| Cyanora (Cyanora_EyesOfBelga) | 0.704 | 1.111 | 0.717 |
| DG Film Look (DGFilmLook_DannyG) | 0.289 | 0.387 | 0.360 |
| Dawn Hues (DawnHues_Leno) | 0.491 | 0.738 | 0.411 |
| E100 (E100) | 0.697 | 1.057 | 0.743 |
| EmotionalB&W (EmotionalB&W_Wazika) | 0.328 | 0.148 | 0.241 |
| EuroFilmBW (EuroFilmBW_Vincent) | 0.384 | 0.172 | 0.259 |
| F400H (F400H) | 0.356 | 0.473 | 0.353 |
| Filmic (FILMICBW) | 0.284 | 0.104 | 0.261 |
| FILMSTILLFilmic (FILMSTILLFilmic) | 0.427 | 0.664 | 0.465 |
| FIlmstill's Nostalgic Negative (FIlmstill's_Nostalgic_Negative) | 0.537 | 0.806 | 0.531 |
| FProvia100F (FProvia100F) | 0.483 | 0.756 | 0.552 |
| FSol100 (FSol100) | 0.407 | 0.593 | 0.500 |
| FadedBlue (FadedBlue_Hinami) | 0.420 | 0.541 | 0.367 |
| Fern (Fern_IanHarland) | 0.319 | 0.428 | 0.414 |
| Film Pop (FilmPop_Leno) | 0.777 | 1.078 | 0.603 |
| Filmic (Filmic_Fabio) | 0.402 | 0.566 | 0.445 |
| FilmstilGoldmatic (FilmstilGoldmatic) | 0.484 | 0.725 | 0.429 |
| Filmstill's ARTE B&W (Filmstill's_ARTE_B&W) | 0.305 | 0.139 | 0.366 |
| Filmstill's Astia (Filmstill's_Astia) | 0.428 | 0.627 | 0.459 |
| Filmstill's Classic Neg (Filmstill's_Classic_Neg) | 0.626 | 0.849 | 0.578 |
| Filmstill's Portra (Filmstill's_Portra) | 0.779 | 1.155 | 0.604 |
| Filmstill's Velvia (Filmstill's_Velvia) | 0.437 | 0.654 | 0.460 |
| Glow Up (GlowUp_Preston) | 0.563 | 1.009 | 0.548 |
| Glow (Glow_IanHarland) | 0.320 | 0.507 | 0.412 |
| Golden Brown (GoldenBrownSiinapse) | 0.421 | 0.613 | 0.487 |
| Golden Dusk (GoldenDusk_EmilieH) | 0.564 | 0.896 | 0.469 |
| Golden Hour Glow (GoldenHourGlow_DAnn) | 0.683 | 1.036 | 0.621 |
| Golden Grid (Golden_Grid_LKJ) | 0.633 | 0.947 | 0.604 |
| Green Soul (Green_Soul_Wong) | 0.577 | 0.902 | 0.638 |
| H-1+rossandhisjpegs (H-1+rossandhisjpegs) | 0.573 | 0.856 | 0.612 |
| HKReminisce (HKReminisce_Hiuman) | 0.628 | 1.012 | 0.539 |
| HT Harmony (HT_Harmony_HanaaT) | 0.608 | 0.938 | 0.511 |
| Hazy Memories (HazyMemories_Julia) | 0.367 | 0.502 | 0.359 |
| Heartwarming (Heartwarming_YoheiS) | 0.418 | 0.584 | 0.361 |
| Hidamari (Hidamari_Haruka) | 0.598 | 0.893 | 0.421 |
| Honey Tale (HoneyTale_MASAYA) | 0.399 | 0.608 | 0.461 |
| Honey (Honey_IanHarland) | 0.287 | 0.387 | 0.390 |
| Indoor Harmony (IndoorHarmony_Julia) | 0.372 | 0.501 | 0.316 |
| Japanesque (Japanesque_Arashida) | 0.479 | 0.746 | 0.585 |
| KCHROME (KCHROME) | 0.417 | 0.601 | 0.431 |
| KEktr100 (KEktr100) | 0.439 | 0.632 | 0.454 |
| KG200 (KG200) | 0.364 | 0.523 | 0.359 |
| KG200P1 (KG200P1) | 0.460 | 0.705 | 0.543 |
| KOLORA (KOLORA) | 0.525 | 0.792 | 0.391 |
| KOLORA PUSHED (KOLORA_PUSHED) | 0.519 | 0.772 | 0.427 |
| KP160 (KP160) | 0.414 | 0.576 | 0.350 |
| KP400 (KP400) | 0.452 | 0.674 | 0.393 |
| KP800 (KP800) | 0.585 | 0.862 | 0.583 |
| Kodachrome (Kodachrome) | 0.342 | 0.506 | 0.438 |
| Kota-Green (Kota-Green_TAKASU) | 0.448 | 0.599 | 0.343 |
| L100 (L100) | 0.439 | 0.631 | 0.482 |
| LeicaSTD (LeicaSTD) | 0.383 | 0.576 | 0.408 |
| LeicaVIV (LeicaVIV) | 0.426 | 0.623 | 0.414 |
| LoFi (LoFi) | 0.493 | 0.734 | 0.531 |
| MGA AcrosLike FC (MGA_AcrosLike_FC) | 0.559 | 0.521 | 0.739 |
| MGA BW Portrait FC (MGA_BW_Portrait_FC) | 0.598 | 0.540 | 0.876 |
| MGA EverydayChromeW (MGA_EverydayChromeW) | 0.766 | 1.223 | 0.589 |
| MGA Everyday Chrome (MGA_Everyday_Chrome) | 0.759 | 1.197 | 0.570 |
| MGA Futurist FC (MGA_Futurist_FC) | 0.927 | 1.476 | 0.864 |
| MGA HCM-Street (MGA_HCM-Street) | 0.549 | 0.486 | 1.249 |
| MGA In-An-Instant (MGA_In-An-Instant) | 0.517 | 0.734 | 0.496 |
| MGA In-An-InstantBW (MGA_In-An-InstantBW) | 0.465 | 0.340 | 0.421 |
| MGA Klassic Khrome (MGA_Klassic_Khrome) | 0.532 | 0.776 | 0.459 |
| MGA Kodachrome 2025 (MGA_Kodachrome_2025) | 1.023 | 1.572 | 1.115 |
| MGA LeicaMono FC (MGA_LeicaMono_FC) | 0.620 | 0.537 | 0.542 |
| MGA MonoFilmic FC (MGA_MonoFilmic_FC) | 0.361 | 0.227 | 0.399 |
| MGA Natural FC (MGA_Natural_FC) | 0.604 | 1.040 | 0.681 |
| MGA Nostalgic FC (MGA_Nostalgic_FC) | 0.848 | 1.273 | 1.077 |
| MGA Nostalgic Past (MGA_Nostalgic_Past) | 0.565 | 0.764 | 0.631 |
| MGA OldFilmish FC (MGA_OldFilmish_FC) | 0.791 | 1.184 | 0.955 |
| MGA OldSchool RTP (MGA_OldSchool_RTP) | 0.431 | 0.678 | 0.492 |
| MGA Paintry FC (MGA_Paintry_FC) | 0.876 | 1.434 | 0.842 |
| MGA Pop! (Blue) (MGA_Pop!_(Blue)) | 0.947 | 1.191 | 0.739 |
| MGA Pop! (Green) (MGA_Pop!_(Green)) | 0.972 | 1.434 | 0.721 |
| MGA Pop! (Red) (MGA_Pop!_(Red)) | 1.052 | 1.244 | 0.799 |
| MGA Portra-Fade FC (MGA_Portra-Fade_FC) | 0.718 | 1.002 | 0.499 |
| MGA Portra-Ish FC (MGA_Portra-Ish_FC) | 0.565 | 0.805 | 0.464 |
| MGA Retrofy (MGA_Retrofy) | 1.221 | 1.832 | 1.028 |
| MGA Retrofy 2 (MGA_Retrofy_2) | 1.011 | 1.443 | 0.760 |
| MGA Sandstorm (MGA_Sandstorm) | 0.461 | 0.687 | 0.663 |
| MGA Slide (MGA_Slide) | 0.636 | 1.028 | 0.610 |
| MGA Slide 2 (MGA_Slide_2) | 0.683 | 1.029 | 0.857 |
| MGA Standard MovieT (MGA_Standard_MovieT) | 0.470 | 0.775 | 0.645 |
| MGA Summer Memories (MGA_Summer_Memories) | 1.097 | 1.849 | 0.927 |
| MGA TriX (MGA_TriX) | 0.466 | 0.406 | 0.969 |
| MGA WEZZY (MGA_WEZZY) | 0.909 | 1.529 | 1.114 |
| MNightBlush (MNightBlush_Preston) | 0.549 | 0.811 | 0.419 |
| MOSS (MOSS_Nagisa) | 0.430 | 0.650 | 0.497 |
| MV Green Orange (MV_Green_Orange_Woo) | 0.926 | 1.483 | 0.604 |
| Matte Blue Gray (MatteBlueGray_tanco) | 0.349 | 0.465 | 0.332 |
| MoistureGn (MoistureGn_HirokiN) | 0.480 | 0.668 | 0.506 |
| MoodyGr (MoodyGr_BrittanyK) | 0.672 | 1.015 | 0.598 |
| Moody Shadows (MoodyShadows_Gilmar) | 0.409 | 0.595 | 0.448 |
| MovieG&O (MovieG&O_InstantF) | 0.346 | 0.437 | 0.336 |
| N-3+rossandhisjpegs (N-3+rossandhisjpegs) | 0.438 | 0.653 | 0.492 |
| Nature (Nature_Links) | 0.377 | 0.583 | 0.415 |
| Negative Bu 01a (Negative_Bu_01a) | 0.409 | 0.573 | 0.413 |
| Negative Bu 01b (Negative_Bu_01b) | 0.413 | 0.650 | 0.481 |
| Negative CyBu 01a (Negative_CyBu_01a) | 0.467 | 0.679 | 0.456 |
| Negative CyBu 01b (Negative_CyBu_01b) | 0.430 | 0.655 | 0.476 |
| Negative Cy 01a (Negative_Cy_01a) | 0.485 | 0.671 | 0.410 |
| Negative GnCy 01a (Negative_GnCy_01a) | 0.462 | 0.712 | 0.456 |
| Negative GnCy 01b (Negative_GnCy_01b) | 0.455 | 0.788 | 0.488 |
| Negative RdCy 01a (Negative_RdCy_01a) | 0.466 | 0.658 | 0.424 |
| Negative RdCy 01b (Negative_RdCy_01b) | 0.467 | 0.738 | 0.488 |
| Negative T 01a (Negative_T_01a) | 0.548 | 0.752 | 0.465 |
| Negative T 01b (Negative_T_01b) | 0.535 | 0.805 | 0.518 |
| Negative YeCy 01a (Negative_YeCy_01a) | 0.342 | 0.462 | 0.325 |
| Negative YeCy 02a (Negative_YeCy_02a) | 0.342 | 0.448 | 0.338 |
| Negative YeGn 01a (Negative_YeGn_01a) | 0.565 | 0.857 | 0.474 |
| Negative YeGn 01b (Negative_YeGn_01b) | 0.547 | 0.840 | 0.495 |
| Negative Ye 01a (Negative_Ye_01a) | 0.428 | 0.641 | 0.453 |
| Negative Ye 01b (Negative_Ye_01b) | 0.410 | 0.700 | 0.505 |
| Negative Ye 02a (Negative_Ye_02a) | 0.432 | 0.625 | 0.418 |
| Negative Ye 02b (Negative_Ye_02b) | 0.423 | 0.713 | 0.467 |
| Negative Ye 03a (Negative_Ye_03a) | 0.483 | 0.675 | 0.397 |
| Negative Ye 03b (Negative_Ye_03b) | 0.488 | 0.738 | 0.484 |
| Neon Glow (NeonGlow_BrandonW) | 0.649 | 1.136 | 0.624 |
| NightsLike (NightsLike_Dondre) | 0.353 | 0.470 | 0.500 |
| OptiColour200 (OptiColour200) | 0.468 | 0.674 | 0.468 |
| Painterly Light (PainterlyLight_DAnn) | 0.672 | 1.057 | 0.798 |
| Pale Tale (Pale_Tale_Yuri) | 0.464 | 0.716 | 0.438 |
| PastelNos (PastelNos_TSakai) | 0.466 | 0.714 | 0.538 |
| Pastelpink (Pastelpink_Yuki) | 0.464 | 0.575 | 0.383 |
| PinkWater (PinkWater_HYEYA) | 0.332 | 0.448 | 0.309 |
| PremiumCinema Green (PremiumCinema_Green) | 0.417 | 0.545 | 0.387 |
| Premium Dreamy Mono (Premium_Dreamy_Mono) | 0.331 | 0.134 | 0.407 |
| Premium Dreamy Peep (Premium_Dreamy_Peep) | 0.364 | 0.305 | 0.948 |
| Premium Koda2025 (Premium_Koda2025) | 0.814 | 1.269 | 0.958 |
| Premium Monochrome (Premium_Monochrome) | 0.443 | 0.336 | 0.543 |
| Premium Negative (Premium_Negative) | 0.465 | 0.698 | 0.458 |
| Premium Nostalgic (Premium_Nostalgic) | 0.748 | 1.149 | 0.934 |
| Premium Standard (Premium_Standard) | 0.732 | 1.117 | 0.566 |
| Premium Standard V2 (Premium_Standard_V2) | 0.481 | 0.689 | 0.482 |
| Premium Vivid Norm (Premium_Vivid_Norm) | 0.716 | 1.458 | 0.840 |
| Premium Vivid Punch (Premium_Vivid_Punch) | 0.747 | 1.475 | 0.954 |
| Primary Pop (PrimaryPop_Gilmar) | 0.530 | 0.700 | 0.421 |
| PurpleM (PurpleM_LUIZCLAS) | 0.364 | 0.512 | 0.434 |
| QUIET (QUIET_Nagisa) | 0.405 | 0.641 | 0.421 |
| RedM (RedM_LUIZCLAS) | 0.441 | 0.702 | 0.434 |
| Rose Old Film (RoseOldFilm_hinano) | 0.530 | 0.700 | 0.421 |
| Scott's Gold 200 (Scott's_Gold_200) | 0.603 | 0.868 | 0.494 |
| Scott's Ilford 400 (Scott's_Ilford_400) | 0.311 | 0.119 | 0.338 |
| Scott's Ilford 400 LO (Scott's_Ilford_400_LO) | 0.294 | 0.119 | 0.178 |
| Scott's Ilford 400 MID (Scott's_Ilford_400_MID) | 0.287 | 0.107 | 0.278 |
| Scott's Leiter (Scott's_Leiter) | 0.699 | 1.007 | 0.834 |
| Scott's Leiter CLR (Scott's_Leiter_CLR) | 0.660 | 0.977 | 0.826 |
| Scott's Vintage Film (Scott's_Vintage_Film) | 0.474 | 0.720 | 0.373 |
| Scott's Vintage Film HI (Scott's_Vintage_Film_HI) | 0.519 | 0.788 | 0.417 |
| Setouchi Blue (SetouchiBlue_Noci) | 0.314 | 0.399 | 0.293 |
| ShadeFall (ShadeFall_BrittanyK) | 0.479 | 0.859 | 0.430 |
| Sky Mist Film (SkyMistFilm_hinano) | 0.562 | 0.765 | 0.452 |
| Soft Film (SoftFilm_Leno) | 0.362 | 0.448 | 0.323 |
| SoftGlow (SoftGlow_Harpreet) | 0.351 | 0.528 | 0.437 |
| Soft Vivid (Soft_Vivid_Vijay) | 0.539 | 0.743 | 0.478 |
| SummerShine (SummerShine_Dondre) | 0.329 | 0.416 | 0.336 |
| Summertime (Summertime_Zerletti) | 0.778 | 1.211 | 0.730 |
| Sunkissed Cool (SunkissedCool_Julia) | 0.444 | 0.587 | 0.329 |
| SunkissedWarm (SunkissedWarm_Julia) | 0.444 | 0.587 | 0.329 |
| SunlightHappy (SunlightHappy_DAnn) | 0.530 | 0.807 | 0.570 |
| SunsetFilm (SunsetFilm_JKBoy) | 0.645 | 0.946 | 0.595 |
| Sunset Glow (SunsetGlow_Mikan) | 0.514 | 0.773 | 0.527 |
| Sunset Reset (SunsetReset_Baek) | 0.396 | 0.513 | 0.334 |
| T&O (T&O_BrandonW) | 0.503 | 0.729 | 0.487 |
| Tender Clear (TenderClear_FukaK) | 0.408 | 0.582 | 0.383 |
| TexturedDocmntry (TexturedDocmntry_MS) | 0.421 | 0.634 | 0.582 |
| Turquoise Blue (Turquoise_Blue_Yuki) | 0.369 | 0.513 | 0.397 |
| USAFilmBW (USAFilmBW_Vincent) | 0.615 | 0.456 | 0.423 |
| VINTAGEFla (VINTAGEFla_Fuji) | 0.536 | 0.874 | 0.507 |
| VINTAGEPort (VINTAGEPort_Fuji) | 0.476 | 0.714 | 0.403 |
| VINTAGE FILM (VINTAGE_FILM_Ludwig) | 0.292 | 0.388 | 0.304 |
| Vibrant (Vibrant_Lamoureux) | 0.485 | 0.736 | 0.581 |
| VintageA (VintageA_BrittanyK) | 0.480 | 0.859 | 0.426 |
| VintageM (VintageM_TSakai) | 0.353 | 0.458 | 0.379 |
| Vintage Touch (VintageTouch_Amy) | 0.476 | 0.608 | 0.433 |
| VintageVibe (VintageVibe_Preston) | 0.574 | 0.836 | 0.523 |
| Vitality Film (VitalityFilm_Pmango) | 0.550 | 0.877 | 0.519 |
| WL3 (WL3) | 0.437 | 0.725 | 0.449 |
| WarmDimLight (WarmDimLight_Luna) | 0.524 | 0.734 | 0.477 |
| Warm Portrait (WarmPortrait_Y2) | 0.329 | 0.462 | 0.404 |
| Warm Street (Warm_Street_Ben) | 0.778 | 1.207 | 0.528 |
| WarmtonedPtt (WarmtonedPtt_Wazika) | 0.560 | 0.879 | 0.467 |
| Wedding V1 Colour (Wedding_V1_Colour) | 0.556 | 0.900 | 0.663 |
| Wedding V1 Mono (Wedding_V1_Mono) | 0.344 | 0.153 | 0.390 |
| Winter Hues (Winter_Hues_Eeva) | 0.518 | 0.835 | 0.520 |
| Yuragi (Yuragi_Hinami) | 0.475 | 0.692 | 0.473 |


## Actual Camera Raw spot checks

The three new checks verify applied profile fingerprints and record approximation error: [measurements](y8_acr_validation.json). Bleach Blue / Banding test 1 mean ΔE 0.018; Filmic / Landscape test 1 mean 0.084; Golden Brown / Landscape test 2 mean 0.274. The last exceeds the initial preview-equivalence threshold. A separate full-resolution diagnostic confirmed the cause: transformation after area averaging differs from transformation before averaging. Matching ACR order reduces Golden Brown mean ΔE to 0.0023. No baseline drift was found. Small numerical previews approximate the style; final Lightroom evaluation takes priority. [Diagnostic](preview_2849_diagnosis.json).
