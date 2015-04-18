#! /usr/bin/env python
from __future__ import division, print_function, absolute_import

import bisect
from collections import defaultdict
import random
import string

import numpy as np


_items = ['champion_copper_plus_spark_plug',
          'cheezit_big_original',
          'crayola_64_ct',
          'elmers_washable_no_run_school_glue',
          'expo_dry_erase_board_eraser',
          'feline_greenies_dental_treats',
          'first_years_take_and_toss_straw_cup',
          'genuine_joe_plastic_stir_sticks',
          'highland_6539_self_stick_notes',
          'kong_air_dog_squeakair_tennis_ball',
          'kong_duck_dog_toy',
          'kong_sitting_frog_dog_toy',
          'kyjen_squeakin_eggs_plush_puppies',
          'mark_twain_huckleberry_finn',
          'mead_index_cards',
          'mommys_helper_outlet_plugs',
          'munchkin_white_hot_duck_bath_toy',
          'oreo_mega_stuf',
          'paper_mate_12_count_mirado_black_warrior',
          'rolodex_jumbo_pencil_cup',
          'safety_works_safety_glasses',
          'sharpie_accent_tank_style_highlighters',
          'stanley_66_052',
          'dr_browns_bottle_brush',
          'laugh_out_loud_joke_book']


def _multinomial(probabilites, start=1):
    """Choose integer in [start, start + len(probabilites))
    according to `probabilites`."""
    cum_prob = np.cumsum(probabilites)
    rv = random.random()
    return start + bisect.bisect_left(cum_prob, rv)

def fill_bins_and_work_order(seed=None, probabilites=None):
    """Create random order and shelve filling, following the contest
    rules.


    Rules:
    >= 2 bins will only contain one item. Both picking targets.
    >= 2 bins will contain two items. One item from each bin will be picking target.
    >= 2 bins will contain >= 3 items. One from each will be a picking target.

    There can be duplicate items. In that case, pick either, but not
    both.

    A single item will be designated to be picked. I assume every
    order has exactly the same number of objects as number of bins

    Parameters
    ==========
    seed : int
        Seed random functions for reproducible results. Defaults to
        None

    probabilites : list of floats
        Likelyhood of filling up bins with [1, 2...]  elements the
        bins that aren't determined by the contest rules. Defaults to
        [0.7, 0.2, 0.1], so that there are no bins with more than 3
        elements.

    Returns
    =======
    dict
        Can be dumped into json

    """
    random.seed(seed)
    if probabilites is None:
        probabilites = [0.7, 0.2, 0.1]

    N_bins = 3*4
    bins = ['bin_{}'.format(i.upper()) for i in string.letters[:N_bins]]

    # Let's maker sure generated filling fulfills rules
    n_items = [1, 1, 2, 2, 3, 3]
    # and then fill the rest with a random number of objects. The
    # rules say that many bins will have a single item, so we actually
    # generate more single item bins
    n_items += [_multinomial(probabilites) for _ in range(N_bins - len(n_items))]
    contents = defaultdict(list)
    random.shuffle(bins)
    for bin, n_item in zip(bins, n_items):
        for _ in range(n_item):
            contents[bin].append(random.choice(_items))

    # And after filling the shelves, we just choose a random element
    # from each bin
    order = [{"bin": bin,
              "item": random.choice(contents[bin])} for bin in sorted(bins)]

    data = {}
    data["bin_contents"] = dict(contents)
    data["work_order"] = order

    return data


if __name__ == '__main__':
    import argparse
    import ast
    import json


    parser = argparse.ArgumentParser()
    parser.add_argument("filename", type=str,
                        help="filename to save the json order to")
    parser.add_argument("--probabilites", "-p", default=None,
                        help="Quote delimited list of probabilites. Eg"
                        " \"[0.5, 0.2, 0.2, 0.1]\". Determines the likelyhood"
                        " of filling up with [1, 2...]  elements the bins that"
                        " aren't determined by the contest rules. Defaults"
                        " to [0.7, 0.2, 0.1], so that there are no bins with"
                        " more than 3 elements.")
    parser.add_argument("--seed", "-s", default=None)

    args = parser.parse_args()


    if args.probabilites is not None:
        args.probabilites = ast.literal_eval(args.probabilites)
        if abs(sum(args.probabilites) - 1) > 1e-14:
            raise ValueError("Please make sure your probabilites add up to 1!")

    d = fill_bins_and_work_order(args.seed, args.probabilites)
    with open(args.filename, 'w') as f:
        json.dump(d, f, indent=4, separators=(',', ': '), sort_keys=True)
