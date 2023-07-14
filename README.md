
# vsicon - unofficial VS2022 Font Icon
![](banner-light.png#gh-light-mode-only)
![](banner-dark.png#gh-dark-mode-only)


Available for download in [Releases](/releases). Demo at https://sakiodre.github.io/vsicon/.

## Usage
To use in webpages:
```html
<link rel="stylesheet" type="text/css" href="vsicon.css"/>
<i class="vsicon vsicon-Debug"></i>
```

## Icon source
The icon pack is available for download [on Microsoft website](https://www.microsoft.com/en-us/download/details.aspx?id=35825), and licensed under [MICROSOFT SOFTWARE LICENSE TERMS](/font-src/Visual%20Studio%202022%20Image%20Library/Visual%20Studio%202022%20Image%20Library%20EULA.rtf).

## Build instruction
1. Install [nanoemoji](https://github.com/googlefonts/nanoemoji) either via git or pypi:  `pip install nanoemoji`
2. Downgrade [skia-pathops](https://github.com/fonttools/skia-pathops) to 0.7.4 ([see why](https://github.com/googlefonts/picosvg/issues/304)): `pip install skia-pathops==0.7.4`
3. Run `python build.py`