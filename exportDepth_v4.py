# This script exports a SCALED DENSE depth map, after MESH stage has been completed, and a scale has been entered.
# If no scale is entered, depth maps have relative scale.
# Exported depth maps are the same size as the original images in the chunk, but compressed. 
# This level of compression does not affect the accuracy needed for color correciton.
# Derya Akkaynak

import Metashape
import os
from os.path import exists

# General setup
app = Metashape.app
chunk = app.document.chunk

# Set output folder
outputFolder = app.getExistingDirectory("Select Output Folder")

# Is the model scaled? If not assign scale of 1
if chunk.transform.scale is None:
    scale = 1
else:
	scale = chunk.transform.scale

# For tracking progress
totalCameras = len(chunk.cameras)
completedCameras = 0

# Export depth maps for all aligned cameras in chunk 
for camera in chunk.cameras:

    # Progress tracking
    completedCameras += 1
    infoHeading = "[" + str(completedCameras) + "/" + str(totalCameras) + "] [" + camera.label + "] "

    # Don't lock the UI
    app.update()

	# [Guard] If the image is already aligned, skip
    imageIsAligned = camera.transform
    if not imageIsAligned: 
        print (infoHeading + "Camera is not aligned. Skipping...")
        continue
        
    # [Guard] If the depth map exists in the output folder, skip
    outputPath = os.path.join(outputFolder, camera.label + "_depth" + ".tif")
    depthMapAlreadyExists = exists(outputPath)
    if depthMapAlreadyExists:
        print (infoHeading + "Depth map has already been exported. Skipping...")
        continue
    
    # Generate depth map
    # Determine depth and compression
    depth = chunk.model.renderDepth(camera.transform, camera.sensor.calibration)
    depth = depth * scale
    depth = depth.convert(" ","F16")
    compression = Metashape.ImageCompression()
    compression.tiff_compression = Metashape.ImageCompression().TiffCompressionDeflate
    
    # Export depth map
    # Save depth to specified folder
    depth.save(outputPath, compression = compression)

    # Note completion
    print(infoHeading + "Depth map exported.")
