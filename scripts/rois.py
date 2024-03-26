import omero
from omero.cli import cli_login
from omero.gateway import BlitzGateway
from omero_rois import mask_from_binary_image
import pathlib
import re
from tifffile import tifffile


"""
This script has a lot of dependencies, best create a micromamba env for it:

# install micromamba
"${SHELL}" <(curl -L micro.mamba.pm/install.sh)

# add alias
echo "alias mm=micromamba" >> ~/.bashrc
source ~/.bashrc

# create env and install stuff
mm env create -n cli python=3.10
mm activate cli
mm install omero-py
pip install ome_model scikit-image omero-rois
"""


PROJECT_NAME = "idr0151-clark-patterning/experimentA"
PATH = "/uod/idr/filesets/idr0151-clark-patterning"

RGBA = (255, 255, 0, 128)
IMAGE_NAME_PATTERN = re.compile(r".+_\d\d\d.tif$")


def get_mask_path(image_name, all_paths):
    mask_image_name = image_name.replace(".tif", "_mask.tif")
    for path in all_paths:
        if str(path).lower().endswith(mask_image_name):
            return path
    return None


def getImages(conn):
    proj = conn.getObject('Project', attributes={'name': PROJECT_NAME})
    for dataset in proj.listChildren():
        for img in dataset.listChildren():
            if IMAGE_NAME_PATTERN.match(img.getName()):
                yield img


def save_roi(conn, im, roi):
    us = conn.getUpdateService()
    im = conn.getObject('Image', im.id)
    roi.setImage(im._obj)
    print(f"Save ROI for image {img.getName()}")
    us.saveAndReturnObject(roi)


def delete_rois(conn, im):
    result = conn.getRoiService().findByImage(im.id, None)
    to_delete = []
    for roi in result.rois:
        to_delete.append(roi.getId().getValue())
    if to_delete:
        print(f"Deleting existing {len(to_delete)} rois on image {im.name}.")
        conn.deleteObjects("Roi", to_delete, deleteChildren=True, wait=True)


def create_roi(img, mask_paths):
    mask_path = get_mask_path(img.getName(), mask_paths)
    if not mask_path:
        print(f"Could not find mask image for {img.getName()}")
        return None
    mask_image = tifffile.imread(mask_path)
    roi = omero.model.RoiI()
    mask = mask_from_binary_image(mask_image>0, rgba=RGBA, z=None, c=None, t=None, text=None)
    roi.addShape(mask)
    return roi


with cli_login() as cli:
    conn = BlitzGateway(client_obj=cli.get_client())
    root = pathlib.Path(PATH)
    mask_paths = list(root.rglob("*.tif"))
    for img in getImages(conn):
        delete_rois(conn, img)
        roi = create_roi(img, mask_paths)
        if roi:
            save_roi(conn, img, roi)
