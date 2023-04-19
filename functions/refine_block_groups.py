# ---------------------------------------------------------------------------
# fun_block_groups.py
# Authors: Mariel Sorlien
# Last updated: 2023-04-19
# Python 3.7
#
# Description: Joins additional dataset to block group data, saves file to scratch folder
# ---------------------------------------------------------------------------

import arcpy


def block_group_spatial_join(target_features, join_features, output_features):
    gis_temp = arcpy.env.scratchFolder + '/blockgroup_join.shp'

    print('Adding spatial join')
    arcpy.analysis.SpatialJoin(target_features=target_features,
                               join_features=join_features,
                               out_feature_class=gis_temp,
                               match_option='LARGEST_OVERLAP')
    print('Saving data')
    arcpy.management.CopyFeatures(in_features=gis_temp,
                                  out_feature_class=output_features)
