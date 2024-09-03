import folium

# Cria um mapa centrado em uma localização específica
mapa = folium.Map(location=[45.5236, -122.6750], zoom_start=13)

# Adiciona um marcador com um popup
folium.Marker([45.5236, -122.6750], popup='Este é um popup!').add_to(mapa)

# Salva o mapa em um arquivo HTML
mapa.save('mapa_com_popup.html')
