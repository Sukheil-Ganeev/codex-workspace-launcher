CREATE INDEX idx_locations_type ON locations(location_type);
CREATE INDEX idx_routes_start_location ON routes(start_location_id);
CREATE INDEX idx_gps_tracking_vehicle ON gps_tracking(vehicle_id);
CREATE INDEX idx_gps_tracking_time ON gps_tracking(tracked_at DESC);
CREATE INDEX idx_geofence_events_geofence ON geofence_events(geofence_id);
CREATE INDEX idx_poi_type ON poi(poi_type);
