import json

def process_graph_config(config_file):
    # Cargar la configuración desde el archivo JSON
    with open(config_file, 'r') as f:
        config = json.load(f)

    # Procesar la configuración
    processed_config = {
        "orientation_horizontal": config["orientation_horizontal"],
        "num_graphs": config["num_graphs"],
        "graph_proportions": config["graph_proportions"],
        "max_curves": config["max_curves"],
        "graphs": []
    }

    for graph_config in config["graphs"]:
        processed_graph = {
            "title": graph_config["title"],
            "type": graph_config["type"],
            "x_label": graph_config["x_label"],
            "y_label": graph_config["y_label"],
            "x_limits": graph_config["x_limits"],
            "y_limits": graph_config["y_limits"],
            "show_grid": graph_config["show_grid"],
            "tick_spacing": graph_config["tick_spacing"],
            "curves": []
        }

        for curve in graph_config["curves"]:
            if curve["enabled"]:
                processed_graph["curves"].append({
                    "name": curve["name"],
                    "label": curve["label"],
                    "color": curve["color"]
                })

        processed_config["graphs"].append(processed_graph)

    return processed_config
