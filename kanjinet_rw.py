#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr  2 14:07:52 2021

@author: Bent Harnist

This is a collection of functions serving to handle kanji
graph building, editing, writing and reading using networkx and jamdict.
"""

import os
import networkx as nx
from jamdict import Jamdict
import pandas as pd
import numpy as np


jmd = Jamdict()


def gen_dag(kanji_list, soft=True, loners=True):
    '''
    Generates a DAG from the kanji list given.

    Parameters
    ----------
    kanji_list : Iterable of Strings
        List of kanji to generate the DAG.
    soft : Boolean, optional
        Do we allow radical search outside kanjis
        specified in the kanji_list? The default is True.
    loners: Boolean, optional
        Do we include single nodes without edges?
        The default is True.

    Returns
    -------
    dig: NetworkX DiGraph

    '''

    dig = nx.DiGraph()
    krad = jmd.krad

    for k in kanji_list:
        neighPool = krad[k]
        for n in neighPool:
            if not dig.has_edge(n,k) and n != k:
                if soft:
                    dig.add_edge(n,k)
                elif n in kanji_list:
                    dig.add_edge(n,k)
                else:
                    continue
        if not neighPool and loners:
            dig.add_node(k)

    return dig

def get_kanji_properties(kanji_list):
    '''
    Lookup all characters contained in the list in
    kanjidic2, then iterates over them and add
    available properties to a dataframe.

    Parameters
    ----------
    kanji_list : Iterable of Strings
        List of kanji whose properties we want to fetch.

    Returns
    -------
    pandas.DataFrame
        Contains literal and kanji properties from kanjidic2.

    '''

    kanji_str = "".join(kanji_list)
    kanji_iter = jmd.lookup(kanji_str).chars

    literal = []
    stroke_count = []
    grade = []
    freq = []
    jlpt = []

    for k in kanji_iter:
        if k.literal: literal.append(k.literal)
        if k.stroke_count: stroke_count.append(int(k.stroke_count))
        if k.grade: grade.append(int(k.grade))
        if k.freq: freq.append(int(k.freq))
        if k.jlpt: jlpt.append(int(k.jlpt))

    return pd.DataFrame({'literal': pd.Series(literal, dtype=np.dtype("O")),
                         'stroke_count': pd.Series(stroke_count, dtype=np.dtype("int32")),
                         'grade': pd.Series(grade, dtype=np.dtype("int32")),
                         'freq':pd.Series(freq, dtype=np.dtype("int32")),
                         'jlpt':pd.Series(jlpt, dtype=np.dtype("int32"))})


def add_kanji_properties(G, property_names, df):
    '''
    Add properties to nodes (kanjis) in the network.

    Parameters
    ----------
    G : NetworkX DiGraph
        Kanji Network (DAG).
    property_names : List of Strings
        Names of kanji properties we want to add.
    df : Pandas.DataFrame
        Dataframe with a df['literal'] column corresponding
        to kanji literals we are interested in, with
        other column representing kanji attributes.

    Returns
    -------
    G : NetworkX DiGraph
        Network having node properties added.

    '''

    for node in G.nodes():
        ls = []
        for p in property_names:
            try:
                row_number = df[df['literal'] == node].index[0]
                ls.append((p, df[p][row_number]))
            except (KeyError, IndexError):
                continue
        prop_dic = dict(ls)
        nx.set_node_attributes(G,{node: prop_dic})

    return G



def write_file_gexf(dag, f_name):
    '''
    Write the kanji network to an GEXF file on disk.

    Parameters
    ----------
    dag : NetworkX DiGraph
        The graph to write.
    f_name : String
        The file name to write the file.

    Returns
    -------
    None.

    '''

    os.makedirs("data", exist_ok=True)
    path_full = os.path.join("data", f_name)
    nx.write_gexf(dag, path_full)


def read_file_gexf(f_name):
    '''
    Read the kanji network file from an GEXF file on disk.

    Parameters
    ----------
    f_name : String
        The file name to read the file.

    Returns
    -------
    dig : NetworkX DiGraph

    '''

    path_full = os.path.join("data", f_name)
    dig = nx.read_gexf(path_full)

    return dig


