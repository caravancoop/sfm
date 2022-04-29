var UnitMaps = {
  onEachFeature: function(feature, layer){
    layer.bindPopup(feature.properties.name);
  },
  getFeatureType: function(location) {
    if (location.properties.feature_type) {
      return location.properties.feature_type
    } else {
      return location.properties.sfm['location:geo_type']
    }
  },
  initializeMap: function(L, element, locations, attribution) {
    var map = L.map(element);

    L.tileLayer(
      'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: attribution,
        detectRetina: true
      }
    ).addTo(map);

    var features = L.featureGroup();

    $.each(locations.features, function (_, location) {
      const featureType = UnitMaps.getFeatureType(location)

      if (['node', 'point'].indexOf(featureType) >= 0) {
        // Coordinates are (x, y) and Leaflet expects (y, x). reverse() modifies
        // an array inplace, so create a copy as not to mutate the source data,
        // then reverse the coordinates before passing to the Marker method.
        // More: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/reverse
        var leafletCoordinates = location.geometry.coordinates.slice();
        leafletCoordinates.reverse();
        features.addLayer(
          L.marker(leafletCoordinates).bindPopup(location.properties.name)
        )
      } else if (['boundary', 'way', 'relation', 'poly', 'line'].indexOf(featureType) >= 0) {
        features.addLayer(
          L.geoJson(location, {onEachFeature: UnitMaps.onEachFeature})
        ).setStyle(
          {fillOpacity: location.properties.feature_type === 'way' ? 0 : 0.25}
        )
      } else {
        console.error('Got unexpected feature type ' + location.properties.feature_type + ' for location ' + location.properties.name)
      }
    });

    features.addTo(map);

    map.fitBounds(features.getBounds(), {
      'maxZoom': 11,
      'padding': [20, 20]
    });
  }
} || {};
