

As user i want to to have the possibility to like images inside a directory.
An during a directory view , see which images have a like.

@https://www.figma.com/design/XU4hU74Z50sNcRJlLpfMBY/Untitled?node-id=1-2&m=dev

# UI
Add a new wrapper to the gallery : `frame_body.py`:
- likes-navigator
- current gallery scrollable grid

`Liked image-boxes` becomes a accent border, and not the current white border.
By double clik on a image-box will be added the image to the likes array properly .json file.
If file not exists by first click, then will be created.


# COMPONENT likes-navigator
A 100% height viewport.
REnder a min. 1px line based by each image in directory represented in the gallery.
If a image has a like , the line will be filled by the accent color as in design.
The like-navigatos is not scrollable, but is a clickable element (or lines inside) that allow the gallery to scroll til the seleced image or make the selected/clicked image visible in gallery view.
The like-navigator has a small darker opacity black element overlayed that represents in whick position the current gallery scroll is positioned.

# LIKE STorages
In same path as the viewer.exe should be created a `./viewer-storage`.
The directory contains 1 json file by directory where likes are created. 
The json path is the full path hashed, pseudo example: `C:\Users\mengi\pros\_yo\picture-bulk\output` -> `765127623zg32g2g234.json`
```
./viwer-storage
    - favourites.json
    - 765127623zg32g2g234.json
```

# Json content

`
{
 "full_path":"C:\Users\mengi\pros\_yo\picture-bulk\output",
 "likes":[
    "temp_1781244410531.jpg",
    "temp_1781244425491.jpg"
 ]
}
`

# NEW FEATURE OPTIONS
In the show_options menu `src/frame.py`
add a separator and these options:
- show likes navigator
- clear directory likes: removes the likes json file

