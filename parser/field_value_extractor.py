from parser.kmeans_cluster import perform_kmeans_clustering
from parser.text_extractor import extract_text_regions
from box import Box


def extract_field_values(image_file_path, fields):
    extracted_fields = []
    text_regions = extract_text_regions(image_file_path)
    for field in fields:
        field_region = get_field_region(text_regions, field['name'])
        if field_region is None:
            continue
        value = extract_field_value(field['name'], field_region.position, field['value_position'], text_regions)
        if value is None:
            continue
        extracted_fields.append({'field': field['name'], 'value': value})
    return extracted_fields


def get_field_region(text_regions, field_name):
    if len(field_name.split()) > 1:
        field_region = find_all_field_region(text_regions, field_name)
        if field_region is not None:
            return field_region
    else:
        for text_region in text_regions:
            if field_name.lower() == text_region.content.lower():
                return text_region
    return None


def find_all_field_region(text_regions, field_name):
    identified_field_regions = []
    identified_field_positions = []
    field_names = field_name.lower().split()
    for text_region in text_regions:
        if text_region.content.lower() in field_names:
            identified_field_regions.append(text_region)
            identified_field_positions.append(
                [float(text_region.position[0][0]), float(text_region.position[0][1])])
    if len(identified_field_regions) <= 0:
        return None
    field_regions = []
    while True:
        if len(identified_field_regions) < len(field_names):
            return None
        clustered_labels = perform_kmeans_clustering(identified_field_positions)
        first_cluster = [field_region for index, field_region in enumerate(identified_field_regions) if
                         clustered_labels[index] == 0]
        second_cluster = [field_region for index, field_region in enumerate(identified_field_regions) if
                          clustered_labels[index] == 1]
        if len(first_cluster) == len(field_names):
            if verify_all_fields_presence(first_cluster, field_names):
                field_regions = first_cluster
                break
        if len(second_cluster) == len(field_names):
            if verify_all_fields_presence(second_cluster, field_names):
                field_regions = second_cluster
                break
        if verify_all_fields_presence(first_cluster, field_names):
            identified_field_positions = []
            identified_field_regions = []
            for region in first_cluster:
                identified_field_regions.append(region)
                identified_field_positions.append(
                    [float(region.position[0][0]), float(region.position[0][1])])
            continue
        elif verify_all_fields_presence(second_cluster, field_names):
            identified_field_positions = []
            identified_field_regions = []
            for region in second_cluster:
                identified_field_regions.append(region)
                identified_field_positions.append(
                    [float(region.position[0][0]), float(region.position[0][1])])
        else:
            return None
    if len(field_regions) <= 0:
        return None
    field_region = field_regions[0]
    for next_field in field_regions[1:]:
        field_region = merge_regions(field_region, next_field)

    return field_region


def verify_all_fields_presence(cluster, field_names):
    cluster_region_content = [region.content.lower() for region in cluster]
    for field_name in field_names:
        if field_name not in cluster_region_content:
            return False
    return True


def merge_regions(region, next_region):
    content = region.content + " " + next_region.content
    confidence = region.confidence if region.confidence > next_region.confidence else next_region.confidence
    position = [[0, 0], [0, 0]]
    for j in [0, 1]:
        position[0][j] = region.position[0][j] if region.position[0][j] < next_region.position[0][j] else \
            next_region.position[0][j]
        position[1][j] = region.position[1][j] if region.position[1][j] > next_region.position[1][j] else \
            next_region.position[1][j]
    field_region = {
        'content': content,
        'confidence': confidence,
        'position': [(position[0][0], position[0][1]), (position[1][0], position[1][1])]
    }
    return Box(field_region)


def extract_field_value(field_value, field_position, value_position, text_regions):
    values = get_possible_field_values(field_value, field_position, value_position, text_regions)
    if value_position == "below":
        values = sort_by_y_axis(values)
    return values[0].content if len(values) > 0 else None


def sort_by_y_axis(values):
    return sorted(values, key=lambda x: (x.position[0][1]))


def sort_by_text_content(values):
    return sorted(values, key=lambda x: x.content)


def get_possible_field_values(field_value, field_position, value_position, text_regions):
    regions = []
    for text_region in text_regions:
        if text_region.content != field_value:
            if value_position == "below":
                if is_text_region_below(field_position, text_region):
                    regions.append(text_region)
    return regions


def is_text_region_below(field_position, text_region):
    if text_region.position[0][0] >= field_position[0][0]:
        if text_region.position[0][1] >= field_position[0][1]:
            if text_region.position[0][0] < field_position[1][0]:
                if text_region.position[0][1] >= field_position[1][1]:
                    return True
    return False
    # A,222,380
    # B,268,379
    # C,184,1628
    # D,1194,1782
    # E,1216,2050
    # F,862,3281
    # G,559,3361
    # A,222,380
    # B,184,1628
    # C,1194,1782
    # D,1216,2050
    # E,1270,2050
    # F,1198,2095
    # G,1182,2140
    # H,1305,2141
    # I,1130,2185
    # J,1281,2185
    # K,862,3281
    # L,559,3361
