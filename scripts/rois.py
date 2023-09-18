import omero
from omero.cli import cli_login
from omero.gateway import BlitzGateway
from omero.gateway import ColorHolder
from omero_rois import mask_from_binary_image
from omero.model import MaskI
from omero.rtypes import (
    rdouble,
    rint,
    rstring
)


RGBA = (255, 255, 0, 128)


def getMaskImages(conn):
    proj = conn.getObject('Project', attributes={'name': 'idr0151-clark-patterning/experimentA'})
    for dataset in proj.listChildren():
        for img in dataset.listChildren():
            if "_mask.tif" in img.getName():
                yield img


def getImage(conn, maskImg):
    name = maskImg.getName().replace("_mask", "")
    proj = conn.getObject('Project', attributes={'name': 'idr0151-clark-patterning/experimentA'})
    for dataset in proj.listChildren():
        for img in dataset.listChildren():
            if img.getName() == name:
                return img


def save_roi(conn, im, roi):
    us = conn.getUpdateService()
    im = conn.getObject('Image', im.id)
    roi.setImage(im._obj)
    us.saveAndReturnObject(roi)


def delete_rois(conn, im):
    result = conn.getRoiService().findByImage(im.id, None)
    to_delete = []
    for roi in result.rois:
        to_delete.append(roi.getId().getValue())
    if to_delete:
        print(f"Deleting existing {len(to_delete)} rois on image {im.name}.")
        conn.deleteObjects("Roi", to_delete, deleteChildren=True, wait=True)


def create_roi(img):
    plane = img.getPrimaryPixels().getPlane()
    roi = omero.model.RoiI()
    mask = mask_from_binary_image(plane > 0, rgba=RGBA, z=None, c=None, t=None, text=None)
    roi.addShape(mask)
    return roi


with cli_login() as cli:
    conn = BlitzGateway(client_obj=cli.get_client())
    for maskImg in getMaskImages(conn):
        img = getImage(conn, maskImg)
        print(f"{maskImg.getName()} - {img.getName()}")
        delete_rois(conn, img)
        roi = create_roi(maskImg)
        save_roi(conn, img, roi)
