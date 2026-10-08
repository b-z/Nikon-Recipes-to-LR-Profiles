# Original synthetic example

These small sample pairs were created for this project; they contain no Nikon recipe or user photograph.

```sh
nikon-recipes-lr fit --adobe-samples examples/adobe.json \
  --nx-samples examples/toy-style.json --name "Toy affine look" \
  --author "Project synthetic example" --grid 4 --output toy.xmp --report toy-report.json
nikon-recipes-lr audit toy.xmp
```

The target is an affine RGB transform, not an NX Studio export. This checks the end-to-end sample→fit→XMP→audit path without vendor applications. For a real recipe, replace both files with paired 16-bit Adobe RGB chart measurements from NX and Adobe.
