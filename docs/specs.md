# Description

Create a portable application for windows.
The applications is a image viewer.
The user can select and navidate throwugh widnows directories and by select , the images of the directory will be displayed.


# Tech Stack

| Part                   | Tech                                 |
|------------------------|--------------------------------------|
| App and UI             | Python + PySide6                     |
| Read and visualization | Qt (`QImageReader`, `QGraphicsView`) |
| Portable distribution  | PyInstaller `--onedir`               |

# UI 

https://www.figma.com/design/mWJ8rPtN8XA2ifsZ7QbZrd/Untitled?node-id=1-3&m=dev


The whole viewport can be splited in Frames.
There is no limit for the number of frames.
Frames takes 100% height of the viewport, and takes horizontally so many place as possible:
- x2 frames -> 50%
- x3 frames _> 33%
- etc..

Frames images container is scrollable.
Frame Parts:
- header: contains tools, buttons and path input
- gallery (image grid container, scrollable)

## header
- favourites modal button: opens the float favorites list modal
- directory selection button: opens a windows navigation window
- path input: selected path, user can copy and paste path
- layout modal button: opens the layout options modal
- "more options" modal button: opens a modal with different options/actions

## gallery
Gallery shows images-boxes that contains the image/ image-thumbnail
The gallery has different visualizations modes:
- grid: square boxes, that can be resized by user with "shift + mouse wheel"
- full width images-boxes: boxes will be expanded til frame width, images takes 100% of width, mainte aspectRatio

## Modal Favoutites
Simple list of saved favourites path:
Ellipsed path visible, just las segment
Numered List

## Modal Layout
Options:
- Grid
- Expand width

# More options Modal
- Save/remove from favourites
- Close frame
- Open in windows: opens native windows window
- Show images name: display absolute positioned in image box the image name and extension
- New frame: open a new Frame near the right side of the current panel