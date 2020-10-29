from hoseParser import computeIndicators

def computeIndicatorsFromSnapShot(parsed, time):
    dic = computeIndicators(parsed, time)
    timeObj = dic['time']
    dic['time'] = (dic['time']['hour'] * 3600 + dic['time']['minute'] * 60 + dic['time']['second']) / 3600
    dic['timeObj'] = timeObj

    return dic