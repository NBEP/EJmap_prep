# ---------------------------------------------------------------------------
# fun_block_groups.py
# Authors: Mariel Sorlien
# Last updated: 2023-04-12
# Python 3.7
#
# Description: Assigns town names, watershed names to block groups;
#   drops block groups with no land area
# ---------------------------------------------------------------------------

def refine_block_groups(add_town_names, add_watershed_names, add_study_area, clip_to_land,
                        gis_block_groups, gis_towns, gis_watersheds, gis_study_area):
    if add_town_names is True:
        print('Adding town names')

    if add_watershed_names is True:
        print('Adding watershed names')

    if add_study_area is True:
        print('Adding study area')

    if clip_to_land is True:
        print('Dropping all block groups with 0 acres land')

    print('Saving updated block groups')
