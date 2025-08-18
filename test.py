import folium
from folium.plugins import Draw

# Starting point for the map (example: Riga center)
m = folium.Map(location=[56.95, 24.1], zoom_start=12)

# Add drawing tools (rectangle, polygon, circle, etc.)
draw = Draw(
    export=True,   # <-- enables "Export" button to download drawn shapes as GeoJSON
    filename='bad_regions.geojson',
    position='topleft',
    draw_options={
        'polyline': False,
        'circlemarker': False
    },
    edit_options={'edit': True}
)
draw.add_to(m)

# Save map as HTML
m.save("draw_bad_regions.html")

print("✅ Open 'draw_bad_regions.html' in your browser, draw regions, click 'Export'.")
print("You'll get a GeoJSON file with coordinates of bad regions.")

