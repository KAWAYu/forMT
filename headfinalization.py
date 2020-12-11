#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import xml.etree.ElementTree as ET


def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('--tree')
    parser.add_argument('--output')
    parser.add_argument('--height', default=pow(10, 8), type=int)
    return parser.parse_args()


def hfereorder(node, h):
    if node.tag == 'tok':
        return [node.text]
    elif node.tag == 'cons':
        tail = []
        if node.tail is not None and node.tail.strip():
            tail = [node.tail.strip()]
        if len(node) == 1:
            return hfereorder(node[0], h)
        else:
            left_child = hfereorder(node[0], h-1)
            right_child = hfereorder(node[1], h-1)
            if node.attrib['cat'] == 'COOD':
                return left_child + right_child + tail
            elif h > 0 and node.attrib['head'] == node[0].attrib['id']:
                return right_child + left_child + tail
            else:
                return left_child + right_child + tail
    else:
        hfe_snt = []
        for child in node:
            hfe_snt += hfereorder(child, h)
        return hfe_snt


def headFinalize(sentence, h):
    tree = ET.fromstring(sentence)
    if tree.attrib['parse_status'] != 'success':
        return
    return hfereorder(tree, h)


def main():
    args = parse()
    total = 0
    success = 0
    with open(args.tree) as fin, open(args.output, 'w') as fout:
        for line in fin:
            total += 1
            hfe = headFinalize(line.strip(), args.height)
            if hfe is not None:
                success += 1
                fout.write(' '.join(hfe) + '\n')
    print(f'{success} sentences were head-finalized.\n({total - success} sentences were parse error)')


if __name__ == '__main__':
  main()
