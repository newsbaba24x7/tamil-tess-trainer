# Fonts used in the two trained models

V1 = `tam_multifont` (188 styles), V2-research = `tam_v2_research` (276 styles, includes restricted fonts). Error rates are character error rates on V2-research's 2,309 held-out rendered lines (text never used in training), read by the stock `tam` model, V1 and V2. Each family has only about 7 test lines per style, so single-style families are rough. "Old letters" names the OpenType feature V2-research used to draw pre-1978 letter shapes ("default" = the font always draws them).

| Family | Source | Licence | V1 styles | V2-research styles | Test lines | Stock | V1 | V2-research | Notes |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| Madurai | Agam Type Foundry | CC-BY-4.0 | 3 | 3 | 21 | 32.9% | 1.3% | 2.5% |  |
| AkrutiTml1 | Akruti | GPL | 2 | 2 | 14 | 2.4% | 0.9% | 1.9% |  |
| AkrutiTml2 | Akruti | GPL | 2 | 2 | 14 | 3.6% | 2.3% | 2.9% |  |
| Droid Sans Tamil | Android (Droid) | Apache-2.0 | 2 | 2 | 14 | 0.8% | 0.3% | 0.7% |  |
| GIST-TMOTAbhirami | C-DAC GIST | Non-commercial use only (C-DAC) | – | 2 | 14 | 39.9% | 10.1% | 9.3% | non-commercial; new in V2-research |
| GIST-TMOTAmala | C-DAC GIST | Non-commercial use only (C-DAC) | – | 2 | 14 | 10.5% | 0.8% | 1.0% | non-commercial; new in V2-research |
| GIST-TMOTAppar | C-DAC GIST | Non-commercial use only (C-DAC) | – | 2 | 14 | 8.2% | 0.3% | 0.3% | non-commercial; new in V2-research |
| GIST-TMOTChanakya | C-DAC GIST | Non-commercial use only (C-DAC) | – | 4 | 28 | 0.7% | 0.5% | 0.5% | non-commercial; new in V2-research |
| GIST-TMOTChandra | C-DAC GIST | Non-commercial use only (C-DAC) | – | 2 | 14 | 2.8% | 0.0% | 0.0% | non-commercial; new in V2-research |
| GIST-TMOTHeena | C-DAC GIST | Non-commercial use only (C-DAC) | – | 2 | 14 | 3.5% | 0.7% | 1.2% | non-commercial; new in V2-research |
| GIST-TMOTKalyani | C-DAC GIST | Non-commercial use only (C-DAC) | – | 2 | 14 | 20.9% | 3.1% | 1.1% | non-commercial; new in V2-research |
| GIST-TMOTKamal | C-DAC GIST | Non-commercial use only (C-DAC) | – | 4 | 28 | 3.0% | 1.5% | 0.8% | non-commercial; new in V2-research |
| GIST-TMOTKannadasan | C-DAC GIST | Non-commercial use only (C-DAC) | – | 2 | 14 | 6.4% | 1.4% | 1.1% | non-commercial; new in V2-research |
| GIST-TMOTKannagi | C-DAC GIST | Non-commercial use only (C-DAC) | – | 2 | 14 | 9.8% | 1.8% | 1.1% | non-commercial; new in V2-research |
| GIST-TMOTKomala | C-DAC GIST | Non-commercial use only (C-DAC) | – | 2 | 14 | 1.2% | 0.0% | 0.0% | non-commercial; new in V2-research |
| GIST-TMOTKrishnan | C-DAC GIST | Non-commercial use only (C-DAC) | – | 1 | 7 | 19.9% | 14.7% | 14.1% | non-commercial; new in V2-research |
| GIST-TMOTKumudam | C-DAC GIST | Non-commercial use only (C-DAC) | – | 1 | 7 | 17.2% | 8.3% | 8.9% | non-commercial; new in V2-research |
| GIST-TMOTLalitha | C-DAC GIST | Non-commercial use only (C-DAC) | – | 4 | 28 | 3.0% | 1.9% | 0.8% | non-commercial; new in V2-research |
| GIST-TMOTMadhura | C-DAC GIST | Non-commercial use only (C-DAC) | – | 1 | 7 | 93.3% | 101.4% | 90.9% | non-commercial; new in V2-research |
| GIST-TMOTMina | C-DAC GIST | Non-commercial use only (C-DAC) | – | 1 | 7 | 7.9% | 5.3% | 2.0% | non-commercial; new in V2-research |
| GIST-TMOTNambi | C-DAC GIST | Non-commercial use only (C-DAC) | – | 4 | 28 | 3.4% | 1.0% | 1.0% | non-commercial; new in V2-research |
| GIST-TMOTPadma | C-DAC GIST | Non-commercial use only (C-DAC) | – | 2 | 14 | 3.6% | 0.2% | 0.2% | non-commercial; new in V2-research |
| GIST-TMOTParvathi | C-DAC GIST | Non-commercial use only (C-DAC) | – | 1 | 7 | 31.1% | 23.1% | 22.2% | non-commercial; new in V2-research |
| GIST-TMOTPattinathar | C-DAC GIST | Non-commercial use only (C-DAC) | – | 4 | 28 | 7.0% | 4.5% | 4.3% | non-commercial; new in V2-research |
| Chemmozhi Comic | Chemmozhi (ICTA.lk) | GPL-2.0 | 1 | 1 | 7 | 1.3% | 0.9% | 0.9% |  |
| Chemmozhi Paranar | Chemmozhi (ICTA.lk) | GPL-2.0 | 1 | 1 | 7 | 1.6% | 1.1% | 0.6% |  |
| Chemmozhi Thendral | Chemmozhi (ICTA.lk) | GPL-2.0 | 1 | 1 | 7 | 0.0% | 0.0% | 0.0% |  |
| Chemmozhi Thenee | Chemmozhi (ICTA.lk) | GPL-2.0 | 1 | 1 | 7 | 0.8% | 0.4% | 0.8% |  |
| Chemmozhi Times | Chemmozhi (ICTA.lk) | GPL-2.0 | 1 | 1 | 7 | 3.0% | 0.4% | 0.9% |  |
| Chemmozhi Vaigai | Chemmozhi (ICTA.lk) | GPL-2.0 | 1 | 1 | 7 | 0.5% | 0.5% | 1.0% |  |
| Mukta Malar | Ek Type (Google Fonts) | OFL-1.1 | 7 | 7 | 98 | 1.1% | 0.8% | 0.9% | old letters: ss04 |
| Aaram | Enathu (Tharique Azeez) | OFL-1.1 | 1 | 1 | 7 | 16.1% | 1.8% | 1.4% |  |
| Neythal | Enathu (Tharique Azeez) | OFL-1.1 | 1 | 1 | 7 | 8.4% | 0.4% | 0.0% |  |
| Anek Tamil | Google Fonts | OFL-1.1 | 8 | 12 | 168 | 5.6% | 1.9% | 1.7% | old letters: ss01 |
| Arima | Google Fonts | OFL-1.1 | 7 | 7 | 97 | 3.8% | 3.0% | 3.0% | old letters: ss02 |
| Baloo Thambi 2 | Google Fonts | OFL-1.1 | 5 | 5 | 35 | 0.2% | 0.3% | 0.2% |  |
| Catamaran | Google Fonts | OFL-1.1 | 9 | 9 | 126 | 2.5% | 1.9% | 1.3% | old letters: ss02 |
| Coiny | Google Fonts | OFL-1.1 | 1 | 1 | 7 | 5.4% | 2.9% | 2.9% |  |
| Google Sans | Google Fonts | OFL-1.1 | 6 | 6 | 42 | 0.4% | 0.7% | 0.3% |  |
| Hind Madurai | Google Fonts | OFL-1.1 | 5 | 5 | 70 | 1.0% | 0.4% | 0.2% | old letters: hlig |
| Karla Tamil Inclined | Google Fonts | OFL-1.1 | 2 | 2 | 14 | 0.4% | 0.6% | 0.6% | old letters: default |
| Karla Tamil Upright | Google Fonts | OFL-1.1 | 2 | 2 | 14 | 0.0% | 0.0% | 0.2% | old letters: default |
| Kavivanar | Google Fonts | OFL-1.1 | 1 | 1 | 7 | 0.8% | 0.8% | 0.4% |  |
| Meera Inimai | Google Fonts | OFL-1.1 | 1 | 1 | 7 | 0.0% | 0.5% | 0.5% |  |
| Oi | Google Fonts | OFL-1.1 | 1 | 1 | 7 | 36.4% | 8.6% | 9.1% |  |
| Pavanam | Google Fonts | OFL-1.1 | 1 | 1 | 7 | 0.0% | 0.0% | 0.0% |  |
| Post No Bills Jaffna | Google Fonts | OFL-1.1 | 6 | 6 | 84 | 5.7% | 3.2% | 3.2% | old letters: ss01 |
| Tiro Tamil | Google Fonts | OFL-1.1 | 2 | 2 | 28 | 2.2% | 0.3% | 0.2% | held out (test only); old letters: dlig |
| Noto Sans Tamil | Google Noto | OFL-1.1 | 4 | 15 | 105 | 2.5% | 2.5% | 2.5% |  |
| Noto Serif Tamil | Google Noto | OFL-1.1 | 4 | 26 | 182 | 5.5% | 4.8% | 4.7% |  |
| TABUni-Tamil021 | Gopi (higopi.com) | GPL | 1 | 1 | 7 | 17.0% | 2.2% | 2.7% |  |
| TABUni-Tamil032 | Gopi (higopi.com) | GPL | 1 | 1 | 7 | 4.1% | 0.0% | 0.5% |  |
| TAMUni-Tamil042 | Gopi (higopi.com) | GPL | 1 | 1 | 7 | 28.1% | 4.6% | 6.0% |  |
| TAMUni-Tamil046 | Gopi (higopi.com) | GPL | 1 | 1 | 7 | 10.0% | 3.8% | 4.8% |  |
| TAMUni-Tamil150 | Gopi (higopi.com) | GPL | 1 | 1 | 7 | 41.4% | 11.1% | 16.7% |  |
| TAMUni-Tamil195 | Gopi (higopi.com) | GPL | 1 | 1 | 7 | 43.2% | 12.8% | 20.5% |  |
| TAU-kaviri | Kadugu (P S Ranganathan) | Free use and distribution | 1 | 1 | 7 | 10.3% | 3.8% | 4.9% |  |
| TAU-kollidam | Kadugu (P S Ranganathan) | Free use and distribution | 1 | 1 | 7 | 13.0% | 1.9% | 2.7% |  |
| TAU-palar | Kadugu (P S Ranganathan) | Free use and distribution | 1 | 1 | 7 | 11.9% | 2.3% | 1.9% |  |
| TAU-ponni | Kadugu (P S Ranganathan) | Free use and distribution | 1 | 1 | 7 | 2.4% | 1.5% | 1.5% |  |
| TAU-porunai | Kadugu (P S Ranganathan) | Free use and distribution | 1 | 1 | 7 | 4.9% | 2.2% | 2.2% |  |
| TAU-pothigai | Kadugu (P S Ranganathan) | Free use and distribution | 1 | 1 | 7 | 9.5% | 10.1% | 8.3% |  |
| TAU-thamirabarani | Kadugu (P S Ranganathan) | Free use and distribution | 1 | 1 | 7 | 0.6% | 0.0% | 1.2% |  |
| Lohit Tamil | Lohit (Red Hat/Fedora) | OFL-1.1 | 1 | 1 | 7 | 0.0% | 0.0% | 0.0% |  |
| Lohit Tamil Classical | Lohit (Red Hat/Fedora) | OFL-1.1 | 1 | 1 | 7 | 0.0% | 0.0% | 0.0% | old letters: default |
| Latha | Microsoft (Windows font) | proprietary | 1 | 1 | 7 | 1.0% | 0.5% | 0.0% | not for release |
| Yaldevi Jaffna | Mooniak | OFL-1.1 | – | 6 | 84 | 4.7% | 2.5% | 2.4% | old letters: ss01; new in V2-research |
| Auvaiyar | NLCI | OFL-1.1 | 4 | 4 | 28 | 4.7% | 0.5% | 1.1% |  |
| ThiruValluvar | NLCI | OFL-1.1 | 4 | 4 | 28 | 3.3% | 0.9% | 1.0% |  |
| Samyak Tamil | Samyak (Debian fonts-samyak) | GPL-3.0+ with font exception | 1 | 1 | 7 | 1.8% | 0.6% | 0.0% |  |
| TAMu_Kadambri | TAMu (Kamban Software) | GPL-2.0 | 1 | 1 | 7 | 1.6% | 2.7% | 2.7% |  |
| TAMu_Kalyani | TAMu (Kamban Software) | GPL-2.0 | 1 | 1 | 7 | 1.0% | 1.0% | 0.5% |  |
| TAMu_Maduram | TAMu (Kamban Software) | GPL-2.0 | 1 | 1 | 7 | 1.4% | 0.0% | 0.0% |  |
| TSCu_Times | TSCu | GPL-2.0 | 1 | 1 | 7 | 3.5% | 1.3% | 1.8% |  |
| TAU-Achu | Tamil Virtual Academy | GPL-2.0+ (TVA) | 2 | 2 | 14 | 12.4% | 0.5% | 1.6% |  |
| TAU-Barathi | Tamil Virtual Academy | GPL-2.0+ (TVA) | 4 | 4 | 28 | 2.5% | 1.5% | 0.9% |  |
| TAU-Ezhil | Tamil Virtual Academy | GPL-2.0+ (TVA) | 3 | 3 | 21 | 7.2% | 1.9% | 1.6% |  |
| TAU-Kabilar | Tamil Virtual Academy | GPL-2.0+ (TVA) | 4 | 4 | 28 | 3.8% | 0.4% | 0.7% |  |
| TAU-Kambar | Tamil Virtual Academy | GPL-2.0+ (TVA) | 4 | 4 | 28 | 13.7% | 4.8% | 5.4% | held out (test only) |
| TAU-Kaveri | Tamil Virtual Academy | GPL-2.0+ (TVA) | 4 | 4 | 28 | 5.9% | 2.6% | 2.7% |  |
| TAU-Kurinji | Tamil Virtual Academy | GPL-2.0+ (TVA) | 3 | 3 | 21 | 4.4% | 0.8% | 0.6% |  |
| TAU-Malar | Tamil Virtual Academy | GPL-2.0+ (TVA) | 3 | 3 | 21 | 9.0% | 1.2% | 1.2% |  |
| TAU-Marutham | Tamil Virtual Academy | GPL-2.0+ (TVA) | 3 | 3 | 21 | 5.5% | 4.5% | 5.1% |  |
| TAU-Mullai | Tamil Virtual Academy | GPL-2.0+ (TVA) | 3 | 3 | 21 | 3.2% | 1.1% | 0.6% |  |
| TAU-Neythal | Tamil Virtual Academy | GPL-2.0+ (TVA) | 3 | 3 | 21 | 19.8% | 1.9% | 1.2% |  |
| TAU-Nilavu | Tamil Virtual Academy | GPL-2.0+ (TVA) | 3 | 3 | 21 | 16.5% | 0.8% | 1.3% |  |
| TAU-Paalai | Tamil Virtual Academy | GPL-2.0+ (TVA) | 2 | 2 | 14 | 2.2% | 0.2% | 0.2% |  |
| TAU-Urai | Tamil Virtual Academy | GPL-2.0+ (TVA) | 2 | 2 | 14 | 7.3% | 1.1% | 1.8% |  |
| TAU-Valluvar | Tamil Virtual Academy | GPL-2.0+ (TVA) | 4 | 4 | 28 | 2.8% | 0.6% | 0.8% |  |
| Uni Ila.Sundaram | Uni Ila.Sundaram Fonts Project | OFL-1.1 | 20 | 20 | 140 | 9.8% | 2.9% | 3.1% | style -20 held out |
| uniAmma | installed by you (origin unknown) | unknown | 3 | 3 | 21 | 12.5% | 2.5% | 3.3% | not for release |
| **Total: 91 families** | | | **188** | **276** | | | | | |
