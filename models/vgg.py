"""VGG11/13/16/19 in Pytorch."""
import torch
import torch.nn as nn

kernel_size=3
cfg = {
    'VGG11': [64, 'M', 128, 'M', 256, 256, 'M', 512, 512, 'M', 512, 512, 'M'],
    'VGG13': [64, 64, 'M', 128, 128, 'M', 256, 256, 'M', 512, 512, 'M', 512, 512, 'M'],
    'VGG16': [64, 64, 'M', 128, 128, 'M', 256, 256, 256, 'M', 512, 512, 512, 'M', 512, 512, 512, 'M'],
    'VGG19': [64, 64, 'M', 128, 128, 'M', 256, 256, 256, 256, 'M', 512, 512, 512, 512, 'M', 512, 512, 512, 512, 'M'],

}


class VGG(nn.Module):
    def __init__(self, vgg_name,batchnorm=None,num_classes=10, deconv=None,delinear=None,channel_deconv=None):
        super(VGG, self).__init__()
        self.deconv = deconv
        self.batchnorm = batchnorm
            
        if channel_deconv:
            self.channel_deconv = channel_deconv()
        self.features = self._make_layers(cfg[vgg_name])
        
        if delinear:
            self.classifier = delinear(512, num_classes)
        else:
            self.classifier= nn.Linear(512,num_classes)

    def forward(self, x):
        out = self.features(x)
        if hasattr(self,'channel_deconv'):
            out = self.channel_deconv(out)
        out = out.view(out.size(0), -1)
        out = self.classifier(out)
        return out

    def _make_layers(self, cfg):
        layers = []
        in_channels = 3

        if not self.deconv:
            for x in cfg:
                if x == 'M':
                    layers += [nn.MaxPool2d(kernel_size=2, stride=2)]
                else:
                    conv2d = nn.Conv2d(in_channels, x, kernel_size=kernel_size, padding=int(kernel_size/2))
                    if self.batchnorm:
                        layers += [conv2d,
                                   nn.BatchNorm2d(x),
                                   nn.ReLU(inplace=True)]
                    else:
                        print("没有进行BatchNorm")
                        layers += [conv2d, nn.ReLU(inplace=True)]
                    in_channels = x
            layers += [nn.AvgPool2d(kernel_size=1, stride=1)]
        else:
            for x in cfg:
                print("进行了deconv 不涉及BN")
                if x == 'M':
                    layers += [nn.MaxPool2d(kernel_size=2, stride=2)]
                else:
                    if in_channels==3:
                        deconv = self.deconv(in_channels, x,  kernel_size=kernel_size, padding=int(kernel_size/2), freeze=True, n_iter=15)
                    else:
                        deconv=self.deconv(in_channels, x, kernel_size=kernel_size, padding=int(kernel_size/2))
                    layers += [deconv,
                               nn.ReLU(inplace=True)]
                    in_channels = x
            layers += [nn.AvgPool2d(kernel_size=1, stride=1)]
        return nn.Sequential(*layers)

# net = VGG('VGG11')
# x = torch.randn(2,3,32,32)
# print(net(Variable(x)).size())
