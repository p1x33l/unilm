import argparse

import cv2

from ditod import add_vit_config

import torch

from detectron2.config import get_cfg
from detectron2.utils.visualizer import ColorMode, Visualizer
from detectron2.data import MetadataCatalog
from detectron2.engine import DefaultPredictor


def main():
    parser = argparse.ArgumentParser(description="Detectron2 inference script")
    parser.add_argument(
        "--image_path",
        help="Path to input image",
        type=str,
        required=True,
    )
    # check if image path is valid
    print("Checking if image path is valid...")
    try:
        img = cv2.imread(args.image_path)
        if img is None:
            raise FileNotFoundError
    except FileNotFoundError:
        print("Image path is invalid. Please provide a valid path.")
        return
    print("Image path is valid.")
    parser.add_argument(
        "--output_file_name",
        help="Name of the output visualization file.",
        type=str,
    )
    parser.add_argument(
        "--config-file",
        default="configs/quick_schedules/mask_rcnn_R_50_FPN_inference_acc_test.yaml",
        metavar="FILE",
        help="path to config file",
    )
    parser.add_argument(
        "--opts",
        help="Modify config options using the command-line 'KEY VALUE' pairs",
        default=[],
        nargs=argparse.REMAINDER,
    )

    args = parser.parse_args()

    # Step 1: instantiate config
    cfg = get_cfg()
    add_vit_config(cfg)
    cfg.merge_from_file(args.config_file)
    
    # Step 2: add model weights URL to config
    cfg.merge_from_list(args.opts)
    
    # Step 3: set device
    device = "cuda" if torch.cuda.is_available() else "cpu"
    cfg.MODEL.DEVICE = device

    # Step 4: define model
    predictor = DefaultPredictor(cfg)
    
    # Step 5: run inference
    # check if image path valid
    try:
        print("Reading image from", args.image_path)
        img = cv2.imread(args.image_path)
        print("Image shape:", img.shape)
    except Exception as e:
        print(e)
        return

    md = MetadataCatalog.get(cfg.DATASETS.TEST[0])
    if cfg.DATASETS.TEST[0]=='icdar2019_test':
        md.set(thing_classes=["table"])
    else:
        md.set(thing_classes=["text","title","list","table","figure"])

    output = predictor(img)["instances"]
    v = Visualizer(img[:, :, ::-1],
                    md,
                    scale=1.0,
                    instance_mode=ColorMode.SEGMENTATION)
    result = v.draw_instance_predictions(output.to("cpu"))
    result_image = result.get_image()[:, :, ::-1]

    # step 6: save
    cv2.imwrite(args.output_file_name, result_image)

if __name__ == '__main__':
    main()

