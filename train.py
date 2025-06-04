import os
import random
import argparse
import numpy as np
import torch
import torch.optim as optim
from torch.utils.data import DataLoader
import torch.nn.functional as F

from dataloader.dataset import MedicalDataSets
from albumentations.augmentations import transforms
from albumentations.core.composition import Compose
from albumentations import RandomRotate90, Resize

from utils.util import AverageMeter
import utils.losses as losses
from utils.metrics import iou_score

from network.XGDNet import XGDNet
from network.PVT_EMCAD.networks import EMCADNet
from network.CENet import CE_Net_backbone_DAC_without_atrous
from network.CPFNet import CPF_Net
from network.TransUNet import TransUNet, CONFIGS
from network.poly.pvt import PolypPVT

# 在训练开始前添加
import torch.multiprocessing as mp
mp.set_sharing_strategy('file_system')

def seed_torch(seed):
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True
    random.seed(seed)
    np.random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)


seed_torch(41)

parser = argparse.ArgumentParser()
parser.add_argument('--model', type=str, default="poly",
                    choices=["XGDNet", "EMCADNet", "CE_Net", "CPF_Net", "TransUNet", "poly"], help='model')
parser.add_argument('--base_dir', type=str, default=r"D:\PycharmProjects\pythonProject23\XGDNet\data\busi", help='dir')
parser.add_argument('--train_file_dir', type=str, default="busi_train.txt", help='dir')
parser.add_argument('--val_file_dir', type=str, default="busi_val.txt", help='dir')
parser.add_argument('--base_lr', type=float, default=1e-5, help='fixed learning rate of 0.0001')  # 固定学习率为0.0001
parser.add_argument('--batch_size', type=int, default=8, help='batch_size per gpu')
parser.add_argument('--max_epochs', type=int, default=200, help='maximum epoch number to train')
parser.add_argument('--grad_clip', type=float, default=1.0, help='gradient clipping threshold')
args = parser.parse_args()


class WeightedBCEDiceLoss(torch.nn.Module):
    """带权重的BCE+Dice损失，用于处理类别不平衡"""

    def __init__(self, pos_weight=2.0):
        super().__init__()
        self.pos_weight = pos_weight

    def forward(self, input, target):
        # 计算加权BCE损失
        bce = F.binary_cross_entropy_with_logits(
            input, target,
            pos_weight=torch.tensor([self.pos_weight]).cuda()
        )

        # 计算Dice损失
        smooth = 1e-5
        input_sigmoid = torch.sigmoid(input)
        num = target.size(0)
        input_flat = input_sigmoid.view(num, -1)
        target_flat = target.view(num, -1)
        intersection = (input_flat * target_flat)
        dice = (2. * intersection.sum(1) + smooth) / (input_flat.sum(1) + target_flat.sum(1) + smooth)
        dice_loss = 1 - dice.sum() / num

        return 0.5 * bce + dice_loss


def getDataloader():
    img_size = 256
    train_transform = Compose([
        RandomRotate90(),
        transforms.Flip(),
        Resize(img_size, img_size),
        transforms.Normalize(),
    ])

    val_transform = Compose([
        Resize(img_size, img_size),
        transforms.Normalize(),
    ])
    db_train = MedicalDataSets(base_dir=args.base_dir, split="train", transform=train_transform,
                               train_file_dir=args.train_file_dir, val_file_dir=args.val_file_dir)
    db_val = MedicalDataSets(base_dir=args.base_dir, split="val", transform=val_transform,
                             train_file_dir=args.train_file_dir, val_file_dir=args.val_file_dir)
    print("train num:{}, val num:{}".format(len(db_train), len(db_val)))

    trainloader = DataLoader(db_train, batch_size=args.batch_size, shuffle=True,
                             num_workers=8, pin_memory=True, drop_last=True)
    valloader = DataLoader(db_val, batch_size=1, shuffle=False,
                           num_workers=1)
    return trainloader, valloader


def get_model(args):
    if args.model == "XGDNet":
        model = XGDNet()
    elif args.model == "EMCADNet":
        model = EMCADNet()
    elif args.model == "CE_Net":
        model = CE_Net_backbone_DAC_without_atrous(num_classes=1, num_channels=3)
    elif args.model == "CPF_Net":
        model = CPF_Net(classes=1, channels=3)
    elif args.model == "TransUNet":
        config_vit = CONFIGS["R50-ViT-B_16"]
        config_vit.n_classes = 1
        config_vit.n_skip = 3
        config_vit.patches = {}
        config_vit.patches["grid"] = (14, 14)
        model = TransUNet(config_vit, img_size=256, num_classes=1)
    elif args.model == "poly":
        model = PolypPVT()
        # 解冻所有参数，让模型能够学习
        for param in model.parameters():
            param.requires_grad = True
    else:
        model = None
        print("model err")
        exit(0)
    return model.cuda()


def train(args):
    trainloader, valloader = getDataloader()
    model = get_model(args)
    print("train file dir:{} val file dir:{}".format(args.train_file_dir, args.val_file_dir))

    # 使用Adam优化器，固定学习率
    optimizer = optim.Adam(model.parameters(), lr=args.base_lr, betas=(0.9, 0.999))

    # 使用加权损失函数来处理类别不平衡
    criterion = WeightedBCEDiceLoss(pos_weight=2.0).cuda()

    print("{} iterations per epoch".format(len(trainloader)))
    best_iou = 0

    for epoch_num in range(args.max_epochs):
        model.train()
        avg_meters = {
            'loss': AverageMeter(),
            'iou': AverageMeter(),
            'val_loss': AverageMeter(),
            'val_iou': AverageMeter(),
            'SE': AverageMeter(),
            'PC': AverageMeter(),
            'F1': AverageMeter(),
            'ACC': AverageMeter()
        }

        # 训练阶段
        for i_batch, sampled_batch in enumerate(trainloader):
            volume_batch, label_batch = sampled_batch['image'], sampled_batch['label']
            volume_batch, label_batch = volume_batch.cuda(), label_batch.cuda()

            outputs = model(volume_batch)

            # 确保输出和标签的维度匹配
            if outputs.shape != label_batch.shape:
                outputs = F.interpolate(outputs, size=label_batch.shape[2:], mode='bilinear', align_corners=False)

            loss = criterion(outputs, label_batch)

            # 计算指标
            with torch.no_grad():
                iou, dice, _, _, _, _, _ = iou_score(outputs, label_batch)

            optimizer.zero_grad()
            loss.backward()

            # 梯度裁剪
            torch.nn.utils.clip_grad_norm_(model.parameters(), args.grad_clip)

            optimizer.step()

            avg_meters['loss'].update(loss.item(), volume_batch.size(0))
            avg_meters['iou'].update(iou, volume_batch.size(0))

            # 每20个iteration打印一次
            if i_batch % 20 == 0:
                print(f'Epoch [{epoch_num}/{args.max_epochs}] Iter [{i_batch}/{len(trainloader)}] '
                      f'Loss: {loss.item():.4f} IoU: {iou:.4f}')

        # 验证阶段
        model.eval()
        with torch.no_grad():
            for i_batch, sampled_batch in enumerate(valloader):
                input, target = sampled_batch['image'], sampled_batch['label']
                input = input.cuda()
                target = target.cuda()

                output = model(input)

                # 确保输出和标签的维度匹配
                if output.shape != target.shape:
                    output = F.interpolate(output, size=target.shape[2:], mode='bilinear', align_corners=False)

                loss = criterion(output, target)
                iou, _, SE, PC, F1, _, ACC = iou_score(output, target)

                avg_meters['val_loss'].update(loss.item(), input.size(0))
                avg_meters['val_iou'].update(iou, input.size(0))
                avg_meters['SE'].update(SE, input.size(0))
                avg_meters['PC'].update(PC, input.size(0))
                avg_meters['F1'].update(F1, input.size(0))
                avg_meters['ACC'].update(ACC, input.size(0))

        # 打印当前学习率（固定值）
        current_lr = args.base_lr
        print(
            'epoch [%d/%d]  train_loss : %.4f, train_iou: %.4f '
            '- val_loss %.4f - val_iou %.4f - val_SE %.4f - val_PC %.4f - val_F1 %.4f - val_ACC %.4f - lr: %.6f'
            % (epoch_num, args.max_epochs, avg_meters['loss'].avg, avg_meters['iou'].avg,
               avg_meters['val_loss'].avg, avg_meters['val_iou'].avg, avg_meters['SE'].avg,
               avg_meters['PC'].avg, avg_meters['F1'].avg, avg_meters['ACC'].avg, current_lr))

        # 保存最佳模型
        if avg_meters['val_iou'].avg > best_iou:
            if not os.path.exists('./checkpoint'):
                os.mkdir('checkpoint')
            torch.save({
                'epoch': epoch_num,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'best_iou': avg_meters['val_iou'].avg,
            }, 'checkpoint/{}_model_{}.pth'.format(args.model, args.train_file_dir.split(".")[0]))
            best_iou = avg_meters['val_iou'].avg
            print("=> saved best model")

    print(f"Training finished! Best IoU: {best_iou:.4f}")
    return "Training Finished!"


if __name__ == "__main__":
    train(args)