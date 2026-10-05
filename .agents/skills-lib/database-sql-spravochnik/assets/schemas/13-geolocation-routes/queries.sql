SELECT * FROM locations WHERE location_type = 'landmark' ORDER BY name;
SELECT route_name, distance_km, estimated_duration_minutes FROM routes;
SELECT location_id, latitude, longitude, speed_kmh, tracked_at FROM gps_tracking WHERE vehicle_id = 1 ORDER BY tracked_at DESC LIMIT 10;
SELECT geofence_name, event_type, COUNT(*) as event_count FROM geofence_events ge JOIN geofences g ON ge.geofence_id = g.id GROUP BY geofence_name, event_type;
