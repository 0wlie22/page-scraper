import folium
from folium import plugins

# Starting point for the map (example: Riga center)
m = folium.Map(location=[56.95, 24.1], zoom_start=12)

# Add drawing tools (rectangle, polygon, circle, etc.)
draw = plugins.Draw(
    export=True,
    filename='bad_regions.geojson',
    position='topleft',
    draw_options={
        'polyline': False,
        'circlemarker': False
    },
    edit_options={'edit': True}
)
draw.add_to(m)

m.save("draw_bad_regions.html")
