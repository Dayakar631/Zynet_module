from zynet import zynet
from zynet import utils
import numpy as np

def genMnistZynet(dataWidth,sigmoidSize,weightIntSize,inputIntSize):
    model = zynet.model()
    model.add(zynet.layer("flatten",784))
    model.add(zynet.layer("Dense",30,"sigmoid"))
    model.add(zynet.layer("Dense",20,"sigmoid"))
    model.add(zynet.layer("Dense",10,"sigmoid"))
    model.add(zynet.layer("Dense",10,"hardmax"))
    weightArray = utils.genWeightArray('WeightsAndBiases.txt')
    biasArray = utils.genBiasArray('WeigntsAndBiases.txt')
    model.compile(pretrained='Yes',weights=weightArray,biases=biasArray,dataWidth=dataWidth,weightIntSize=weightIntSize,inputIntSize=inputIntSize,sigmoidSize=sigmoidSize)
    zynet.makeXilinxProject('myPro6','xc7z020clg484-1')
    zynet.makeIP('myPro6')
    zynet.makeSystem('myPro6','myBlock3')
    
if __name__ == "__main__":
    genMnistZynet(dataWidth=8,sigmoidSize=10,weightIntSize=4,inputIntSize=1)