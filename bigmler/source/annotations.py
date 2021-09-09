# -*- coding: utf-8 -*-
#
# Copyright 2021 BigML
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""BigMLer - image annotations formatting

"""

import os
import json
import sys
import xml.etree.ElementTree as ET
import re
import glob
import cv2
import ntpath


from zipfile import ZipFile

from bigml.constants import IMAGE_EXTENSIONS


FILE_ATTR = "file"
BBOXES_ATTR = "boxes"


def bigml_coco_file(annotations_dir, annotations_format,
                    output_file=None):
    """Translates from alternative annotations format, like VOC and YOLO to
    the format accepted by BigML

    """

    if output_file is None:
        output_file = os.path.join(annotations_dir, "annotations.json")
    try:
        zipname = annotations_dir.split(os.path.sep)[-1]
    except Exception:
        zipname = "annotated_images"
    filenames = voc_to_cocojson(annotations_dir, output_file) \
        if annotations_format == "VOC" else \
        yolo_to_cocojson(annotations_dir, output_file)

    zipPath = os.path.join(annotations_dir, "%s.zip" % zipname)

    if filenames:
        if not os.path.exists(zipPath):
            zipObj = ZipFile(zipPath, 'w')
            for filename in filenames:
                zipObj.write(filename)
                zipObj.close()
        with open(os.path.join(annotations_dir, "metadata.json"), "w") as \
                metafile:
            meta_info = {"description": ("Transformed file for images"
                                         " annotations in %s" %
                                         annotations_dir),
                         "images_file": zipPath,
                         "annotations": output_file}
            json.dump(meta_info, metafile)
    return metafile


def get_image_info(annotation_root):
    path = annotation_root.findtext('path')
    if path is None:
        filename = annotation_root.findtext('filename')
    else:
        filename = os.path.basename(path)
    img_name = os.path.basename(filename)
    img_id = os.path.splitext(img_name)[0]
    if isinstance(img_id, str):
        img_id = int(re.findall(r'\d+', img_id)[0])

    size = annotation_root.find('size')
    width = int(size.findtext('width'))
    height = int(size.findtext('height'))

    image_info = {
        'filename': filename,
        'height': height,
        'width': width,
        'id': img_id
    }
    return image_info


def get_coco_annotation_from_object(obj, filename, logfile, warnings):
    label = obj.findtext('name')
    bndbox = obj.find('bndbox')
    ## xmin = int(bndbox.findtext('xmin')) - 1
    xmin = int(bndbox.findtext('xmin'))
    ## ymin = int(bndbox.findtext('ymin')) - 1
    ymin = int(bndbox.findtext('ymin'))
    xmax = int(bndbox.findtext('xmax'))
    ymax = int(bndbox.findtext('ymax'))

    ## assert xmax >= xmin and ymax >= ymin, \
    ## f"Box size error !: (xmin, ymin, xmax, ymax): {xmin, ymin, xmax, ymax}"
    ## o_width = xmax - xmin
    ## o_height = ymax - ymin

    # logging possible errors
    if xmin == xmax or ymin == ymax:
        logfile.write(f"Possible bndbox error in {filename}:\n" +
                      f"  min equal to max: (xmin, ymin, xmax, ymax):" +
                      f"  {xmin, ymin, xmax, ymax}\n")
        warnings += 1
    if xmin > xmax or ymin > ymax:
        logfile.write(f"Possible bndbox error in {filename}:\n" +
                      f"  min greater than max: (xmin, ymin, xmax, ymax):" +
                      f"  {xmin, ymin, xmax, ymax}\n")
        warnings += 1

    annotation = {
        'label': label,
        'xmin': xmin,
        'ymin': ymin,
        'xmax': xmax,
        'ymax': ymax
    }
    return annotation, warnings


def yolo_to_cocojson(yolo_dir, output_jsonfile, args):

    ## assume .txt extension for yolo annotation files,
    ## may be input as args
    yolo_extension = '.txt'
    ## extensions of acceptable image files

    output_json_dict = {
        "annotations": []
    }

    output_json_array = []

    filenames = []

    logfile_name = output_jsonfile + ".log"
    with open(logfile_name, "w") as logfile:

        warnings = 0
        message = "Start converting YOLO files in " + yolo_dir + "\n"
        u.log_message(message, args.session_file, console_log=args.verbosity)
        logfile.write("\n%s" % message)

        ## Read yolo annotation txt file
        yolo_file_list = []
        for a_file in os.listdir(yolo_dir):
            if a_file.endswith(yolo_extension):
                # print(os.path.join(yolo_dir, a_file))
                logfile.write(os.path.join(yolo_dir, a_file) + "\n")
                yolo_file_list.append(os.path.join(yolo_dir, a_file))

        logfile.write("\n")
        ## Check if the yolo files (.txt) in the yolo_dir have their
        ## corresponding images, .jpg, .jpeg, .png, etc
        for yolo_filename in yolo_file_list:
            filename_base = os.path.splitext(yolo_filename)[0]
            # print("filename_base: " + filename_base)
            # print(yolo_dir + "/" + filename_base + ".*")
            image_filename = ''

            matched_files = [file for file in
                    glob.glob(filename_base + ".*") if not
                    file.endswith(yolo_extension)]
            if len(matched_files) == 0:
                print(" Warning: no image file for " + yolo_filename +"\n")
                logfile.write(" Warning: no image file for " +
                        yolo_filename +"\n")
            else:
                # print(*matched_files, sep = ", ")
                # print("matched_files length: " + str(len(matched_files)))

                ## traverse the matched file lists to find the image file,
                ## giving a warning each time a matched file is not in the
                ## image_extensions list.
                ## if there are more than one supported image file,
                ## the last one in the matched_file list is used
                for a_file in matched_files:
                    filenames.append(a_file)
                    base, ext = os.path.splitext(a_file)
                    if ext.lower() in IMAGE_EXTENSIONS:
                        image_filename = a_file
                    else:
                        warnings += 1
                        logfile.write("Warning: unknown image file for " +
                                      yolo_filename + "\n")
                        logfile.write(a_file)
                        logfile.write("\n")

            if not image_filename or image_filename.isspace():
                continue

            # print("image_filename: " + image_filename + "\n")
            logfile.write("converting for: " + image_filename + "\n")
            image_file = cv2.imread(image_filename)
            yolo_file = open(yolo_filename, "r")
            yolo_read_lines = yolo_file.readlines()
            yolo_file.close()

            ## using ntpath module to accommodate MS-Windows paths
            #image_filename_base = os.path.basename(image_filename)
            image_filename_base = ntpath.basename(image_filename)
            logfile.write("taking as filename: " + image_filename_base + "\n")

            one_image_dict = {
                ## possible args options for full path or basename
                FILE_ATTR: image_filename_base,
                BBOXES_ATTR: []
            }

            ## yolo format - (label, xc, yc, width, height)
            ## coco format - (label, xmin, ymin, xmax, ymax)
            for yolo_line in yolo_read_lines:
                one_yolo_annotation = yolo_line
                label = one_yolo_annotation.split()[0]

                x_center = float(one_yolo_annotation.split()[1])
                y_center = float(one_yolo_annotation.split()[2])
                width = float(one_yolo_annotation.split()[3])
                height = float(one_yolo_annotation.split()[4])

                float_x_center = image_file.shape[1] * x_center
                float_y_center = image_file.shape[0] * y_center
                float_width = image_file.shape[1] * width
                float_height = image_file.shape[0] * height

                int_x_center = int(float_x_center)
                int_y_center = int(float_y_center)
                int_width = int(float_width)
                int_height = int(float_height)

                round_width = round(float_width)
                round_height = round(float_height)

                ## Yolo uses normalized coordinates to specify
                ## the bonding boxes. [x_center, y_center, width, height]
                ## Because they are normalized, i.e. ratios to the width
                ## and height of the image, they stay the same when the image
                ## is enlarged or shrank. But the bounding boxes may
                ## lose pixels due to rounding.

                ## The following operations try to reverse the effect of
                ## rounding and add a pixel to the bouding box if reasonable.
                x_center_decimal = float_x_center - int(float_x_center)
                y_center_decimal = float_y_center - int(float_y_center)
                #print("xc_decimal=", x_center_decimal, " yc_decimal=",
                #        y_center_decimal, "\n")
                logfile.write("xc_decimal=" + str(x_center_decimal) +
                              " yc_decimal=" + str(y_center_decimal) + "\n")
                if x_center_decimal <= 0.25:
                    round_x_center = int(float_x_center)
                elif x_center_decimal > 0.25 and x_center_decimal <= 0.75:
                    round_x_center = int(float_x_center) + 0.5
                else:
                    round_x_center = int(float_x_center) + 1

                if y_center_decimal <= 0.25:
                    round_y_center = int(float_y_center)
                elif y_center_decimal > 0.25 and y_center_decimal <= 0.75:
                    round_y_center = int(float_y_center) + 0.5
                else:
                    round_y_center = int(float_y_center) + 1

                if round_x_center - int(round_x_center) == 0:
                    if (round(float_width) % 2) == 0:
                        proper_width = round(float_width)
                    else:
                        proper_width = round(float_width) + 1
                else:
                    if (round(float_width) % 2) == 0:
                        proper_width = round(float_width) + 1
                    else:
                        proper_width = round(float_width)

                if round_y_center - int(round_y_center) == 0:
                    if (round(float_height) % 2) == 0:
                        proper_height = round(float_height)
                    else:
                        proper_height = round(float_height) + 1
                else:
                    if (round(float_height) % 2) == 0:
                        proper_height = round(float_height) + 1
                    else:
                        proper_height = round(float_height)


                #print("xc=", x_center, " yc=", y_center, " w=", width,
                #      " h=", height, "\n")
                logfile.write("xc=" + str(x_center) + " yc=" + str(y_center) +
                            " w=" + str(width) + " h=" + str(height) + "\n")
                #print("float_xc=", float_x_center, " float_yc=", float_y_center,
                #      " float_w=", float_width, " float_h=", float_height, "\n")
                logfile.write("float_xc=" + str(float_x_center) + " float_yc=" +
                              str(float_y_center) + " float_w=" +
                              str(float_width) + " float_h=" +
                              str(float_height) + "\n")
                #print("round_xc=", round_x_center, " round_yc=", round_y_center,
                #      " round_w=", round_width, " round_h=", round_height, "\n")
                logfile.write("round_xc=" + str(round_x_center) + " round_yc=" +
                              str(round_y_center) + " round_w=" +
                              str(round_width) + " round_h=" +
                              str(round_height) + "\n")
                #print("round_xc=", round_x_center, " round_yc=", round_y_center,
                #    " proper_w=", proper_width, " proper_h=", proper_height, "\n")
                logfile.write("round_xc=" + str(round_x_center) + " round_yc=" +
                              str(round_y_center) + " proper_w=" +
                              str(proper_width) + " proper_h=" +
                              str(proper_height) + "\n")
                #print("int_xc=", int_x_center, " int_yc=", int_y_center,
                #      " int_w=", int_width, " int_h=", int_height, "\n\n")
                logfile.write("int_xc=" + str(int_x_center) + " int_yc=" +
                              str(int_y_center) + " int_w=" + str(int_width) +
                              " int_h=" + str(int_height) + "\n\n")

                ## x_min = int_x_center - int_width/2
                x_min = int(round_x_center - proper_width/2)
                ## y_min = int_y_center - int_height/2
                y_min = int(round_y_center - proper_height/2)
                ## x_max = x_min + int_width
                x_max = int(x_min + proper_width)
                ## y_max = y_min + int_height
                y_max = int(y_min + proper_height)
                annotation = {
                        'label': label,
                        'xmin': x_min,
                        'ymin': y_min,
                        'xmax': x_max,
                        'ymax': y_max
                        }
                one_image_dict[BBOXES_ATTR].append(annotation)

            # output_json_dict['annotations'].append(one_image_dict)
            output_json_array.append(one_image_dict)

    if warnings > 0:
        message = f"\nThere are {warnings} warnings, " \
                  f"see the log file {logfile_name}\n"
        u.log_message(message, args.session_file, console_log=args.verbosity)

    with open(output_jsonfile, 'w') as f:
        output_json = json.dumps(output_json_array, indent=2)
        f.write(output_json)

    return filenames


def voc_to_cocojson(voc_dir, output_jsonfile, args):
    """Translates annotations from a VOC format, where each image is associated
    to a .xml file that contains one object per associated info. It returns
    the list of images it refers to.

    """
    output_json_dict = {
        "annotations": []
    }

    output_json_array = []

    filenames = []

    annotation_file_list = []
    for file in os.listdir(voc_dir):
        if file.endswith(".xml"):
            annotation_file_list.append(os.path.join(voc_dir, file))
    logfile_name = output_jsonfile + ".log"
    with open(logfile_name, "w") as logfile:

        ## Start bounding_box_id, possible future use, may be input as args
        bndbox_id = 1
        warnings = 0
        message = "Start converting VOC files in " + voc_dir + "\n")
        u.log_message(message, args.session_file, console_log=args.verbosity)
        logfile.write("\n\n%s\n" % message)
        for a_file in annotation_file_list:
            ## Read annotation xml per image
            annotation_tree = ET.parse(a_file)
            annotation_root = annotation_tree.getroot()

            img_info = get_image_info(annotation_root)
            ## img_id for possible future use
            img_id = img_info['id']
            filename = img_info['filename']
            filenames.append(filename)

            ## possible args options for full path or basename
            logfile.write("converting for: " + filename + "\n")
            ## using ntpath module instead of os.path
            ## to accommodate MS-Windows paths
            image_filename_base = ntpath.basename(filename)
            logfile.write("taking as filename: " + image_filename_base + "\n")

            one_image_dict = {
                ## possible args options for full path or basename
                FILE_ATTR: image_filename_base,
                BBOXES_ATTR: []
            }

            for obj in annotation_root.findall('object'):
                annotation, warnings = get_coco_annotation_from_object( \
                    obj, filename, logfile, warnings)
                ## output_json_dict['annotations'].append(ann)
                ## output_json_dict['bboxes'].append(ann)
                one_image_dict[BBOXES_ATTR].append(annotation)
                bndbox_id = bndbox_id + 1

            # output_json_dict['annotations'].append(one_image_dict)
            output_json_array.append(one_image_dict)

    if warnings > 0:
        message = f"\nThere are {warnings} warnings, " \
                f"see the log file {logfile_name}\n"
        u.log_message(message, args.session_file, console_log=args.verbosity)


    with open(output_jsonfile, 'w') as f:
        output_json = json.dumps(output_json_array, indent=2)
        f.write(output_json)

    return filenames
