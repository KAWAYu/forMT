#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
import codecs
import random
import sys

import RIBES


TIME_TO_REPEAT_SUBSAMPLING = 1000
SUBSAMPLE_SIZE = 0


def parse():
    parser = argparse.ArgumentParser(
        description = 'bootstrap with ribes',
        usage = '\n %(prog)s '
            '\n %(prog)s -h'
    )
    parser.add_argument('hypo1', help="hypothesis1 file")
    parser.add_argument('hypo2', help="hypothesis2 file")
    parser.add_argument('ref', help="reference file")
    parser.add_argument('--time_to_repeat_subsampling', '-t_sample', default=TIME_TO_REPEAT_SUBSAMPLING,
        type=int, help="TIME_TO_REPEAT_SUBSAMPLING")
    parser.add_argument('--subsample_size', '-s_sample', default=SUBSAMPLE_SIZE, type=int,
        help="SUBSAMPLE_SIZE")
    args = parser.parse_args()
    return args


def bootstrap_report(data, title, proc):
    subSampleScoreDiffList, subSampleScore1List, subSampleScore2List = bootstrap_pass(data, proc)
    realScore1 = proc(data["ref"], data["hyp1"])
    realScore2 = proc(data["ref"], data["hyp2"])
    scorePValue = bootstrap_pvalue(subSampleScoreDiffList, realScore1, realScore2)
    scoreAvg1, scoreVar1 = bootstrap_interval(subSampleScore1List)
    scoreAvg2, scoreVar2 = bootstrap_interval(subSampleScore2List)
    print("---=== {title} score ===---".format(title=title))
    print("actual score of hypothesis 1: {realScore1}".format(realScore1=realScore1))
    print("95% confidence interval for hypothesis 1 score: {scoreAvg1} +- {scoreVar1}\n-----".format(scoreAvg1=scoreAvg1, scoreVar1=scoreVar1))
    print("actual score of hypothesis 2: {realScore2}".format(realScore2=realScore2))
    print("95% confidence interval for hypothesis 2 score: {scoreAvg2} +- {scoreVar2}\n-----".format(scoreAvg2=scoreAvg2, scoreVar2=scoreVar2))
    print("Assuming that essentially the same system generated the two hypothesis translations (null-hypothesis),")
    print("the probability of actually getting them (p-value) is: {scorePValue}.".format(scorePValue=scorePValue))


def bootstrap_pass(data ,scoreFunc):
    subSampleDiffList, subSample1List, subSample2List = [], [], []
    for i in range(TIME_TO_REPEAT_SUBSAMPLING):
        num_subsample = SUBSAMPLE_SIZE if SUBSAMPLE_SIZE else len(data["hyp1"])
        subSampleIndices = drawWithReplacement(data['size'], num_subsample) # インデックスのリスト取得
        score1 = scoreFunc(data["ref"], data["hyp1"], subSampleIndices)
        score2 = scoreFunc(data["ref"], data["hyp2"], subSampleIndices)
        subSampleDiffList.append(abs(score2 - score1))
        subSample1List.append(score1)
        subSample2List.append(score2)

        if (i + 1) % 10 == 0:
            print('.', end='', file=sys.stderr)
        if (i + 1) % 100 == 0:
            print(i+1, file=sys.stderr)
    if TIME_TO_REPEAT_SUBSAMPLING % 100 != 0:
        print(".{TIME_TO_REPEAT_SUBSAMPLING}", file=sys.stderr)
    return subSampleDiffList, subSample1List, subSample2List


def bootstrap_pvalue(subSampleDiffList, realScore1, realScore2):
    realDiff = abs(realScore2 - realScore1)
    averageSubSampleDiff = sum(subSampleDiffList) / TIME_TO_REPEAT_SUBSAMPLING
    c = 0
    for subSampleDiff in subSampleDiffList:
        if subSampleDiff - averageSubSampleDiff >= realDiff:
            c += 1
    return c / TIME_TO_REPEAT_SUBSAMPLING


def bootstrap_interval(subSampleList):
    sorted_SampleList = sorted(subSampleList)
    lowerIdx = TIME_TO_REPEAT_SUBSAMPLING // 40
    higherIdx = TIME_TO_REPEAT_SUBSAMPLING - lowerIdx - 1
    lower = sorted_SampleList[lowerIdx]
    diff = sorted_SampleList[higherIdx] - lower
    return (lower + 0.5 * diff, 0.5 * diff)


def readAllData(args):
    data = None
    return data


def drawWithReplacement(setSize, num_subsample):
    return [random.randrange(0, setSize) for _ in range(num_subsample)]


def getRibes(ref, hyp, idxs=None):
    evaluator = RIBES.RIBESevaluator()
    REF = RIBES.Corpus(ref) # refsはファイル名らしい
    HYPO = RIBES.Corpus(hyp) # hypもファイル名
    if not idxs:
        idxs = [i for i in range(len(REF))]
    ribes = 0
    for idx in idxs:
        ribes += evaluator.eval([HYPO[idx]], [[REF[idx]]])
    return ribes / len(idxs)


def main():
    args = parse()
    print("reading data;", file=sys.stderr)
    data = {'ref': args.ref, 'hyp1': args.hypo1, 'hyp2': args.hypo2}
    with codecs.open(args.ref, 'r') as fin:
        data.update({'size': len(fin.readlines())})
    print("conparing hypothesis -- this may take some time;", file=sys.stderr)
    bootstrap_report(data, "RIBES", getRibes)


if __name__ == '__main__':
    main()
