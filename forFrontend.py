from hoseParser import computeIndicatorSingleDataPoint

def computeIndicatorsFromSnapShot(parsed, time):
    dic = computeIndicatorSingleDataPoint(parsed, time)
    timeObj = dic['time']
    dic['time'] = (dic['time']['hour'] * 3600 + dic['time']['minute'] * 60 + dic['time']['second']) / 3600
    dic['timeObj'] = timeObj

    return dic